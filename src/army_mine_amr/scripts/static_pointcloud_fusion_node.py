#!/usr/bin/env python3
"""
Static Continuous PointCloud & Sensor Fusion Node
Fuses:
1. Intel RealSense D435 RGB-D Depth Camera PointCloud (/camera/depth/points)
   - Field of view: FRONT sector (87 deg H FOV, 0.15m to 15.0m range, frame: camera_link)
2. 4D GPU LiDAR PointCloud (/lidar4d/points_raw)
   - Field of view: 360 deg azimuth, 16 vertical beams, frame: lidar4d_link

Publishes:
1. /perception/points_fused (sensor_msgs/PointCloud2)
   - Real-time live unified 3D pointcloud combining RealSense forward sector + 4D LiDAR surround.
   - Target frame: base_link
2. /perception/static_continuous_pointcloud (sensor_msgs/PointCloud2)
   - Continuous accumulated static 3D pointcloud registered in fixed world frame (map / odom).
   - Spatial 3D voxel grid downsampling preserves terrain contours, boulders, flowers, and mines
     as a persistent continuous 3D world as the robot explores.
"""

import math
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import tf2_ros
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
import sensor_msgs_py.point_cloud2 as pc2


class StaticPointCloudFusionNode(Node):
    def __init__(self):
        super().__init__('static_pointcloud_fusion_node')
        self.get_logger().info('🚀 Starting Static Continuous PointCloud & Sensor Fusion Node...')

        self.declare_parameter('static_frame', 'map')
        self.declare_parameter('robot_frame', 'base_link')
        self.declare_parameter('voxel_size', 0.08)  # 8cm voxel resolution
        self.declare_parameter('max_static_points', 120000)

        self.static_frame = self.get_parameter('static_frame').value
        self.robot_frame = self.get_parameter('robot_frame').value
        self.voxel_size = float(self.get_parameter('voxel_size').value)
        self.max_static_points = int(self.get_parameter('max_static_points').value)

        # QoS
        qos_reliable = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # TF2 Listener
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Publishers
        self.pub_fused = self.create_publisher(PointCloud2, '/perception/points_fused', qos_reliable)
        self.pub_static = self.create_publisher(PointCloud2, '/perception/static_continuous_pointcloud', qos_reliable)

        # Point cloud buffers (Nx4: x, y, z, intensity)
        self.latest_camera_pts = None
        self.latest_camera_stamp = None
        self.latest_lidar_pts = None
        self.latest_lidar_stamp = None

        # Static 3D Spatial Voxel Map: dict of (vx, vy, vz) -> (x, y, z, intensity)
        self.static_voxel_map = {}

        # Subscriptions
        self.sub_camera = self.create_subscription(
            PointCloud2, '/camera/depth/points', self.camera_callback, qos_reliable
        )
        self.sub_lidar = self.create_subscription(
            PointCloud2, '/lidar4d/points_raw', self.lidar_callback, qos_reliable
        )

        # Periodic Timers
        # Live fusion publisher at 10 Hz
        self.timer_fused = self.create_timer(0.1, self.publish_live_fused)
        # Static continuous accumulator publisher at 2 Hz
        self.timer_static = self.create_timer(0.5, self.publish_static_continuous)

        self.get_logger().info('✅ PointCloud Fusion Node initialized! Topics: /perception/points_fused, /perception/static_continuous_pointcloud')

    def _transform_points(self, coords, tf_msg):
        """Vectorized rigid transform of Nx3 coords using geometry_msgs/TransformStamped."""
        t = tf_msg.transform.translation
        q = tf_msg.transform.rotation
        x, y, z, w = q.x, q.y, q.z, q.w
        R = np.array([
            [1.0 - 2.0 * (y**2 + z**2), 2.0 * (x * y - z * w), 2.0 * (x * z + y * w)],
            [2.0 * (x * y + z * w), 1.0 - 2.0 * (x**2 + z**2), 2.0 * (y * z - x * w)],
            [2.0 * (x * z - y * w), 2.0 * (y * z + x * w), 1.0 - 2.0 * (x**2 + y**2)]
        ], dtype=np.float32)
        T = np.array([t.x, t.y, t.z], dtype=np.float32)
        return coords.dot(R.T) + T

    def camera_callback(self, msg: PointCloud2):
        """Processes RealSense D435 depth points in camera_link (forward FOV)."""
        try:
            coords = pc2.read_points_numpy(msg, field_names=('x', 'y', 'z'), skip_nans=False)
            if coords.size == 0:
                return

            # Extract finite points within valid D435 range (0.15m to 15.0m forward)
            finite_mask = (
                np.isfinite(coords[:, 0]) & np.isfinite(coords[:, 1]) & np.isfinite(coords[:, 2]) &
                (coords[:, 0] > 0.15) & (coords[:, 0] < 15.0)
            )
            valid_coords = coords[finite_mask]
            if len(valid_coords) == 0:
                return

            # Subsample for efficient high-rate fusion (take every 3rd point: ~15,000 points)
            sub_coords = valid_coords[::3]

            # Intensity tag: 255.0 for RealSense Depth
            intensities = np.full((len(sub_coords), 1), 255.0, dtype=np.float32)
            pts_with_int = np.hstack([sub_coords, intensities])

            self.latest_camera_pts = pts_with_int
            self.latest_camera_stamp = msg.header.stamp

            # Accumulate into static continuous map
            self._accumulate_to_static(sub_coords, msg.header.frame_id, 255.0)

        except Exception as e:
            self.get_logger().warn(f'Camera callback error: {e}', throttle_duration_sec=5.0)

    def lidar_callback(self, msg: PointCloud2):
        """Processes 4D LiDAR points in lidar4d_link (360 deg surround)."""
        try:
            coords = pc2.read_points_numpy(msg, field_names=('x', 'y', 'z'), skip_nans=False)
            if coords.size == 0:
                return

            # Filter finite points and self-reflection points (< 0.25m from robot center)
            dists_sq = coords[:, 0]**2 + coords[:, 1]**2
            finite_mask = (
                np.isfinite(coords[:, 0]) & np.isfinite(coords[:, 1]) & np.isfinite(coords[:, 2]) &
                (dists_sq > 0.25**2)
            )
            valid_coords = coords[finite_mask]
            if len(valid_coords) == 0:
                return

            # Intensity tag: 120.0 for 4D LiDAR
            intensities = np.full((len(valid_coords), 1), 120.0, dtype=np.float32)
            pts_with_int = np.hstack([valid_coords, intensities])

            self.latest_lidar_pts = pts_with_int
            self.latest_lidar_stamp = msg.header.stamp

            # Accumulate into static continuous map
            self._accumulate_to_static(valid_coords, msg.header.frame_id, 120.0)

        except Exception as e:
            self.get_logger().warn(f'LiDAR callback error: {e}', throttle_duration_sec=5.0)

    def _accumulate_to_static(self, coords, source_frame, intensity_val):
        """Transforms points into static_frame (map/odom) and adds to spatial voxel grid."""
        target_frame = self.static_frame
        try:
            if not self.tf_buffer.can_transform(target_frame, source_frame, rclpy.time.Time()):
                # Fallback to odom if map is not ready
                if target_frame != 'odom' and self.tf_buffer.can_transform('odom', source_frame, rclpy.time.Time()):
                    target_frame = 'odom'
                else:
                    return

            tf_msg = self.tf_buffer.lookup_transform(target_frame, source_frame, rclpy.time.Time())
            world_pts = self._transform_points(coords, tf_msg)

            # Vectorized voxel grid downsampling
            v_idx = np.floor(world_pts / self.voxel_size).astype(np.int32)
            _, u_idx = np.unique(v_idx, axis=0, return_index=True)
            u_vox = v_idx[u_idx]
            u_pts = world_pts[u_idx]

            for k, pt in zip(map(tuple, u_vox), u_pts):
                self.static_voxel_map[k] = (pt[0], pt[1], pt[2], intensity_val)

            # Cap maximum points in memory
            if len(self.static_voxel_map) > self.max_static_points:
                excess = len(self.static_voxel_map) - self.max_static_points
                keys_to_remove = list(self.static_voxel_map.keys())[:excess]
                for k in keys_to_remove:
                    del self.static_voxel_map[k]

        except Exception:
            pass

    def publish_live_fused(self):
        """Publishes instantaneous live fused PointCloud2 (RealSense FRONT + LiDAR 360) in base_link."""
        fused_list = []

        # 1. RealSense Points -> base_link
        if self.latest_camera_pts is not None:
            try:
                tf_cam = self.tf_buffer.lookup_transform(self.robot_frame, 'camera_link', rclpy.time.Time())
                cam_coords = self.latest_camera_pts[:, :3]
                cam_trans = self._transform_points(cam_coords, tf_cam)
                cam_fused = np.hstack([cam_trans, self.latest_camera_pts[:, 3:4]])
                fused_list.append(cam_fused)
            except Exception:
                pass

        # 2. 4D LiDAR Points -> base_link
        if self.latest_lidar_pts is not None:
            try:
                tf_lidar = self.tf_buffer.lookup_transform(self.robot_frame, 'lidar4d_link', rclpy.time.Time())
                lidar_coords = self.latest_lidar_pts[:, :3]
                lidar_trans = self._transform_points(lidar_coords, tf_lidar)
                lidar_fused = np.hstack([lidar_trans, self.latest_lidar_pts[:, 3:4]])
                fused_list.append(lidar_fused)
            except Exception:
                pass

        if not fused_list:
            return

        all_fused = np.vstack(fused_list).astype(np.float32)

        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        header.frame_id = self.robot_frame

        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name='intensity', offset=12, datatype=PointField.FLOAT32, count=1)
        ]

        cloud_msg = pc2.create_cloud(header, fields, all_fused)
        self.pub_fused.publish(cloud_msg)

    def publish_static_continuous(self):
        """Publishes the continuous accumulated static 3D pointcloud in map/odom frame."""
        if not self.static_voxel_map:
            return

        points = np.array(list(self.static_voxel_map.values()), dtype=np.float32)
        if len(points) == 0:
            return

        # Use map frame if available, else odom
        active_frame = self.static_frame
        try:
            if not self.tf_buffer.can_transform(self.static_frame, 'odom', rclpy.time.Time()):
                active_frame = 'odom'
        except Exception:
            active_frame = 'odom'

        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        header.frame_id = active_frame

        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name='intensity', offset=12, datatype=PointField.FLOAT32, count=1)
        ]

        static_msg = pc2.create_cloud(header, fields, points)
        self.pub_static.publish(static_msg)


def main(args=None):
    rclpy.init(args=args)
    node = StaticPointCloudFusionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
