#!/usr/bin/env python3
"""
High-Performance Gazebo Harmonic (gz sim) to ROS 2 Humble Native Bridge
Bridges:
  - /clock (gz.msgs.Clock -> rosgraph_msgs/Clock)
  - /odom (gz.msgs.Odometry -> nav_msgs/Odometry)
  - /tf (gz.msgs.Pose_V -> tf2_msgs/TFMessage)
  - /scan (gz.msgs.LaserScan -> sensor_msgs/LaserScan)
  - /scan/points (gz.msgs.PointCloudPacked -> sensor_msgs/PointCloud2)
  - /imu/data (gz.msgs.IMU -> sensor_msgs/Imu)
  - /joint_states (gz.msgs.Model -> sensor_msgs/JointState)
  - /cmd_vel (ROS geometry_msgs/Twist -> Gazebo gz.msgs.Twist)
"""

import sys
import rclpy
from rclpy.node import Node as RosNode
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from gz.transport13 import Node as GzNode
from gz.msgs10 import (
    odometry_pb2,
    pose_v_pb2,
    laserscan_pb2,
    pointcloud_packed_pb2,
    imu_pb2,
    model_pb2,
    twist_pb2,
    clock_pb2,
    image_pb2,
    camera_info_pb2,
)

from rosgraph_msgs.msg import Clock
from nav_msgs.msg import Odometry
from tf2_msgs.msg import TFMessage
from geometry_msgs.msg import TransformStamped, Twist
from sensor_msgs.msg import LaserScan, PointCloud2, PointField, Imu, JointState, Image, CameraInfo
from builtin_interfaces.msg import Time


def _extract_frame_ids(header, default_frame="odom", default_child="base_footprint"):
    f_id = default_frame
    c_id = default_child
    if header and hasattr(header, 'data'):
        for kv in header.data:
            val = ""
            if len(kv.value) > 0:
                val = kv.value[0]
            if kv.key == 'frame_id' and val:
                f_id = val
            elif kv.key == 'child_frame_id' and val:
                c_id = val
    return str(f_id), str(c_id)


class GzHarmonicRosBridge(RosNode):
    def __init__(self):
        super().__init__('gz_harmonic_ros_bridge')
        self.get_logger().info('🚀 Starting Native Gazebo Harmonic <-> ROS 2 Bridge...')

        # Reliable QoS profile compatible with SLAM Toolbox, RViz2, Robot State Publisher
        qos_reliable = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        # ROS Publishers
        self.pub_clock = self.create_publisher(Clock, '/clock', qos_reliable)
        self.pub_odom = self.create_publisher(Odometry, '/odom', qos_reliable)
        self.pub_tf = self.create_publisher(TFMessage, '/tf', qos_reliable)
        self.pub_scan = self.create_publisher(LaserScan, '/scan', qos_reliable)
        self.pub_pc = self.create_publisher(PointCloud2, '/lidar4d/points_raw', qos_reliable)
        self.pub_imu = self.create_publisher(Imu, '/imu/data', qos_reliable)
        self.pub_joints = self.create_publisher(JointState, '/joint_states', qos_reliable)

        # Tactical RGB-D Depth Camera Publishers
        self.pub_camera_rgb = self.create_publisher(Image, '/camera/image_raw', qos_reliable)
        self.pub_camera_depth = self.create_publisher(Image, '/camera/depth/image_raw', qos_reliable)
        self.pub_camera_info = self.create_publisher(CameraInfo, '/camera/camera_info', qos_reliable)
        self.pub_camera_points = self.create_publisher(PointCloud2, '/camera/depth/points', qos_reliable)

        # ROS Subscriber for cmd_vel
        self.sub_cmd_vel = self.create_subscription(
            Twist, '/cmd_vel', self.ros_cmd_vel_callback, qos_reliable
        )

        # Gazebo Transport Node
        self.gz_node = GzNode()

        # Gazebo Publisher for cmd_vel
        self.gz_pub_cmd_vel = self.gz_node.advertise('/cmd_vel', twist_pb2.Twist)

        # Gazebo Subscriptions
        self.gz_node.subscribe(clock_pb2.Clock, '/clock', self.gz_clock_callback)
        self.gz_node.subscribe(odometry_pb2.Odometry, '/odom', self.gz_odom_callback)
        self.gz_node.subscribe(pose_v_pb2.Pose_V, '/tf', self.gz_tf_callback)
        self.gz_node.subscribe(laserscan_pb2.LaserScan, '/scan', self.gz_scan_callback)
        self.gz_node.subscribe(pointcloud_packed_pb2.PointCloudPacked, '/scan/points', self.gz_pc_callback)
        self.gz_node.subscribe(imu_pb2.IMU, '/imu/data', self.gz_imu_callback)
        self.gz_node.subscribe(model_pb2.Model, '/joint_states', self.gz_joint_states_callback)

        # Tactical RGB-D Depth Camera Subscriptions
        self.gz_node.subscribe(image_pb2.Image, '/camera/image', self.gz_camera_rgb_callback)
        self.gz_node.subscribe(image_pb2.Image, '/camera/depth_image', self.gz_camera_depth_callback)
        self.gz_node.subscribe(camera_info_pb2.CameraInfo, '/camera/camera_info', self.gz_camera_info_callback)
        self.gz_node.subscribe(pointcloud_packed_pb2.PointCloudPacked, '/camera/points', self.gz_camera_points_callback)

        self.get_logger().info('✅ Gazebo Harmonic Bridge initialized and subscribed to all topics!')

    def _pb_stamp_to_ros(self, pb_stamp):
        t = Time()
        if pb_stamp and (pb_stamp.sec != 0 or pb_stamp.nsec != 0):
            t.sec = pb_stamp.sec
            t.nanosec = pb_stamp.nsec
        else:
            now = self.get_clock().now()
            t = now.to_msg()
        return t

    def gz_clock_callback(self, msg: clock_pb2.Clock):
        ros_msg = Clock()
        ros_msg.clock.sec = msg.sim.sec
        ros_msg.clock.nanosec = msg.sim.nsec
        self.pub_clock.publish(ros_msg)

    def gz_odom_callback(self, msg: odometry_pb2.Odometry):
        ros_msg = Odometry()
        ros_msg.header.stamp = self._pb_stamp_to_ros(msg.header.stamp if msg.HasField('header') else None)

        frame_id, child_frame_id = _extract_frame_ids(
            msg.header if msg.HasField('header') else None,
            default_frame="odom",
            default_child="base_footprint"
        )
        ros_msg.header.frame_id = frame_id
        ros_msg.child_frame_id = child_frame_id

        if msg.HasField('pose'):
            ros_msg.pose.pose.position.x = msg.pose.position.x
            ros_msg.pose.pose.position.y = msg.pose.position.y
            ros_msg.pose.pose.position.z = msg.pose.position.z
            ros_msg.pose.pose.orientation.x = msg.pose.orientation.x
            ros_msg.pose.pose.orientation.y = msg.pose.orientation.y
            ros_msg.pose.pose.orientation.z = msg.pose.orientation.z
            ros_msg.pose.pose.orientation.w = msg.pose.orientation.w

        if msg.HasField('twist'):
            ros_msg.twist.twist.linear.x = msg.twist.linear.x
            ros_msg.twist.twist.linear.y = msg.twist.linear.y
            ros_msg.twist.twist.linear.z = msg.twist.linear.z
            ros_msg.twist.twist.angular.x = msg.twist.angular.x
            ros_msg.twist.twist.angular.y = msg.twist.angular.y
            ros_msg.twist.twist.angular.z = msg.twist.angular.z

        self.pub_odom.publish(ros_msg)

    def gz_tf_callback(self, msg: pose_v_pb2.Pose_V):
        tf_msg = TFMessage()
        for p in msg.pose:
            t = TransformStamped()
            t.header.stamp = self._pb_stamp_to_ros(p.header.stamp if p.HasField('header') else None)

            frame_id, child_frame_id = _extract_frame_ids(
                p.header if p.HasField('header') else None,
                default_frame="odom",
                default_child="base_footprint"
            )

            t.header.frame_id = frame_id
            t.child_frame_id = child_frame_id

            t.transform.translation.x = p.position.x
            t.transform.translation.y = p.position.y
            t.transform.translation.z = p.position.z
            t.transform.rotation.x = p.orientation.x
            t.transform.rotation.y = p.orientation.y
            t.transform.rotation.z = p.orientation.z
            t.transform.rotation.w = p.orientation.w

            tf_msg.transforms.append(t)

        if tf_msg.transforms:
            self.pub_tf.publish(tf_msg)

    def gz_scan_callback(self, msg: laserscan_pb2.LaserScan):
        ros_msg = LaserScan()
        ros_msg.header.stamp = self._pb_stamp_to_ros(msg.header.stamp if msg.HasField('header') else None)
        ros_msg.header.frame_id = msg.frame if msg.frame else 'lidar4d_link'

        ros_msg.angle_min = msg.angle_min
        ros_msg.angle_max = msg.angle_max
        ros_msg.angle_increment = msg.angle_step
        ros_msg.time_increment = 0.0
        ros_msg.scan_time = 1.0 / 15.0
        ros_msg.range_min = msg.range_min
        ros_msg.range_max = msg.range_max

        # If 3D multi-beam lidar (samples * vertical_samples), extract the center horizontal ring (ring 8 of 16) for 2D SLAM
        total_ranges = len(msg.ranges)
        h_samples = msg.count if msg.count > 0 else 720
        if total_ranges > h_samples:
            v_samples = total_ranges // h_samples
            center_ring = v_samples // 2
            start_idx = center_ring * h_samples
            end_idx = start_idx + h_samples
            ros_msg.ranges = list(msg.ranges[start_idx:end_idx])
            if msg.intensities:
                ros_msg.intensities = list(msg.intensities[start_idx:end_idx])
        else:
            ros_msg.ranges = list(msg.ranges)
            ros_msg.intensities = list(msg.intensities)

        self.pub_scan.publish(ros_msg)

    def gz_pc_callback(self, msg: pointcloud_packed_pb2.PointCloudPacked):
        ros_msg = PointCloud2()
        ros_msg.header.stamp = self._pb_stamp_to_ros(msg.header.stamp if msg.HasField('header') else None)
        ros_msg.header.frame_id = 'lidar4d_link'

        ros_msg.height = msg.height
        ros_msg.width = msg.width
        ros_msg.is_bigendian = msg.is_bigendian
        ros_msg.point_step = msg.point_step
        ros_msg.row_step = msg.row_step
        ros_msg.is_dense = msg.is_dense
        ros_msg.data = msg.data

        for f in msg.field:
            rf = PointField()
            rf.name = f.name
            rf.offset = f.offset
            # Gazebo datatype enum is offset by 1 compared to sensor_msgs/PointField
            rf.datatype = f.datatype + 1
            rf.count = f.count
            ros_msg.fields.append(rf)

        self.pub_pc.publish(ros_msg)

    def gz_imu_callback(self, msg: imu_pb2.IMU):
        ros_msg = Imu()
        ros_msg.header.stamp = self._pb_stamp_to_ros(msg.header.stamp if msg.HasField('header') else None)
        ros_msg.header.frame_id = 'imu_link'

        if msg.HasField('orientation'):
            ros_msg.orientation.x = msg.orientation.x
            ros_msg.orientation.y = msg.orientation.y
            ros_msg.orientation.z = msg.orientation.z
            ros_msg.orientation.w = msg.orientation.w

        if msg.HasField('angular_velocity'):
            ros_msg.angular_velocity.x = msg.angular_velocity.x
            ros_msg.angular_velocity.y = msg.angular_velocity.y
            ros_msg.angular_velocity.z = msg.angular_velocity.z

        if msg.HasField('linear_acceleration'):
            ros_msg.linear_acceleration.x = msg.linear_acceleration.x
            ros_msg.linear_acceleration.y = msg.linear_acceleration.y
            ros_msg.linear_acceleration.z = msg.linear_acceleration.z

        self.pub_imu.publish(ros_msg)

    def gz_joint_states_callback(self, msg: model_pb2.Model):
        ros_msg = JointState()
        ros_msg.header.stamp = self._pb_stamp_to_ros(msg.header.stamp if msg.HasField('header') else None)

        for j in msg.joint:
            ros_msg.name.append(j.name)
            if j.axis1 and hasattr(j.axis1, 'position'):
                ros_msg.position.append(j.axis1.position)
            else:
                ros_msg.position.append(0.0)
            if j.axis1 and hasattr(j.axis1, 'velocity'):
                ros_msg.velocity.append(j.axis1.velocity)
            else:
                ros_msg.velocity.append(0.0)
            if j.axis1 and hasattr(j.axis1, 'force'):
                ros_msg.effort.append(j.axis1.force)
            else:
                ros_msg.effort.append(0.0)

        if ros_msg.name:
            self.pub_joints.publish(ros_msg)

    def ros_cmd_vel_callback(self, msg: Twist):
        gz_twist = twist_pb2.Twist()
        gz_twist.linear.x = msg.linear.x
        gz_twist.linear.y = msg.linear.y
        gz_twist.linear.z = msg.linear.z
        gz_twist.angular.x = msg.angular.x
        gz_twist.angular.y = msg.angular.y
        gz_twist.angular.z = msg.angular.z
        self.gz_pub_cmd_vel.publish(gz_twist)

    def gz_camera_rgb_callback(self, msg: image_pb2.Image):
        ros_msg = Image()
        ros_msg.header.stamp = self._pb_stamp_to_ros(msg.header.stamp if msg.HasField('header') else None)
        ros_msg.header.frame_id = 'camera_depth_optical_frame'
        ros_msg.height = msg.height
        ros_msg.width = msg.width
        ros_msg.step = msg.step
        ros_msg.data = msg.data
        ros_msg.is_bigendian = False
        if msg.pixel_format_type == image_pb2.PixelFormatType.RGB_INT8:
            ros_msg.encoding = 'rgb8'
        elif msg.pixel_format_type == image_pb2.PixelFormatType.BGR_INT8:
            ros_msg.encoding = 'bgr8'
        elif msg.pixel_format_type == image_pb2.PixelFormatType.RGBA_INT8:
            ros_msg.encoding = 'rgba8'
        else:
            ros_msg.encoding = 'rgb8'
        self.pub_camera_rgb.publish(ros_msg)

    def gz_camera_depth_callback(self, msg: image_pb2.Image):
        ros_msg = Image()
        ros_msg.header.stamp = self._pb_stamp_to_ros(msg.header.stamp if msg.HasField('header') else None)
        ros_msg.header.frame_id = 'camera_depth_optical_frame'
        ros_msg.height = msg.height
        ros_msg.width = msg.width
        ros_msg.step = msg.step
        ros_msg.data = msg.data
        ros_msg.is_bigendian = False
        if msg.pixel_format_type == image_pb2.PixelFormatType.R_FLOAT32:
            ros_msg.encoding = '32FC1'
        elif msg.pixel_format_type == image_pb2.PixelFormatType.L_INT16:
            ros_msg.encoding = '16UC1'
        else:
            ros_msg.encoding = '32FC1'
        self.pub_camera_depth.publish(ros_msg)

    def gz_camera_info_callback(self, msg: camera_info_pb2.CameraInfo):
        ros_msg = CameraInfo()
        ros_msg.header.stamp = self._pb_stamp_to_ros(msg.header.stamp if msg.HasField('header') else None)
        ros_msg.header.frame_id = 'camera_depth_optical_frame'
        ros_msg.height = msg.height
        ros_msg.width = msg.width
        if msg.HasField('distortion'):
            ros_msg.distortion_model = 'plumb_bob'
            ros_msg.d = [float(x) for x in msg.distortion.k]
        if msg.HasField('intrinsics'):
            k_list = [float(x) for x in msg.intrinsics.k]
            if len(k_list) == 9:
                ros_msg.k = k_list
        if msg.HasField('projection'):
            p_list = [float(x) for x in msg.projection.p]
            if len(p_list) == 12:
                ros_msg.p = p_list
        if len(msg.rectification_matrix) == 9:
            ros_msg.r = [float(x) for x in msg.rectification_matrix]
        self.pub_camera_info.publish(ros_msg)

    def gz_camera_points_callback(self, msg: pointcloud_packed_pb2.PointCloudPacked):
        ros_msg = PointCloud2()
        ros_msg.header.stamp = self._pb_stamp_to_ros(msg.header.stamp if msg.HasField('header') else None)
        ros_msg.header.frame_id = 'camera_link'
        ros_msg.height = msg.height
        ros_msg.width = msg.width
        ros_msg.is_bigendian = msg.is_bigendian
        ros_msg.point_step = msg.point_step
        ros_msg.row_step = msg.row_step
        ros_msg.is_dense = msg.is_dense
        ros_msg.data = msg.data

        for f in msg.field:
            rf = PointField()
            rf.name = f.name
            rf.offset = f.offset
            rf.datatype = f.datatype + 1
            rf.count = f.count
            ros_msg.fields.append(rf)

        self.pub_camera_points.publish(ros_msg)


def main(args=None):
    rclpy.init(args=args)
    node = GzHarmonicRosBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
