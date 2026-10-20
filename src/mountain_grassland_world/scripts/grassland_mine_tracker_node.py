#!/usr/bin/env python3
"""
Mountain Grassland NIPUN Minefield Tracker & Diagnostic Node
Publishes 3D markers, status, and telemetry for the 18 NIPUN minelet locations in the Alpine Mountain Grassland environment.
"""

import os
import math
import yaml
import rclpy
from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory

from geometry_msgs.msg import Pose, PoseArray, Point
from visualization_msgs.msg import Marker, MarkerArray
from std_msgs.msg import String, Header
from std_srvs.srv import Trigger
from nav_msgs.msg import Odometry


class GrasslandMineTrackerNode(Node):
    def __init__(self):
        super().__init__('grassland_mine_tracker_node')

        # Load grassland mine coordinates
        try:
            pkg_share = get_package_share_directory('mountain_grassland_world')
            config_path = os.path.join(pkg_share, 'config', 'grassland_mine_coordinates.yaml')
        except Exception:
            config_path = '/home/nammy/army_mine_bot/src/mountain_grassland_world/config/grassland_mine_coordinates.yaml'

        self.get_logger().info(f'📍 Loading alpine grassland minefield config from: {config_path}')
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
            self.mines = data.get('mines', [])

        self.get_logger().info(f'🎖️ Initialized with {len(self.mines)} NIPUN AP minelet stations in Alpine Grassland World.')

        # Robot pose tracking
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_z = 0.0
        self.robot_pose_received = False

        # Publishers
        self.pose_pub = self.create_publisher(PoseArray, '/mountain_grassland/mines', 10)
        self.marker_pub = self.create_publisher(MarkerArray, '/mountain_grassland/markers', 10)
        self.status_pub = self.create_publisher(String, '/mountain_grassland/status', 10)

        # Subscribers
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        # Periodic timer (2 Hz)
        self.timer = self.create_timer(0.5, self.publish_mines)

    def odom_callback(self, msg: Odometry):
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y
        self.robot_z = msg.pose.pose.position.z
        self.robot_pose_received = True

        # Check proximity to W-formation apex or stations
        for m in self.mines:
            dist = math.sqrt((m['x'] - self.robot_x)**2 + (m['y'] - self.robot_y)**2)
            if dist < 0.60 and not m.get('on_station', False):
                m['on_station'] = True
                self.get_logger().info(f"📍 Station Lock: AMR aligned with [{m['name']}] at distance {dist:.2f}m")

    def publish_mines(self):
        # 1. Publish PoseArray
        pose_array = PoseArray()
        pose_array.header.stamp = self.get_clock().now().to_msg()
        pose_array.header.frame_id = 'odom'

        for m in self.mines:
            p = Pose()
            p.position.x = float(m['x'])
            p.position.y = float(m['y'])
            p.position.z = float(m['z'])
            p.orientation.w = 1.0
            pose_array.poses.append(p)

        self.pose_pub.publish(pose_array)

        # 2. Publish MarkerArray for RViz2
        marker_array = MarkerArray()
        now = self.get_clock().now().to_msg()

        for idx, m in enumerate(self.mines):
            # Disc Cylinder Marker (Coaster Form Factor)
            marker = Marker()
            marker.header.stamp = now
            marker.header.frame_id = 'odom'
            marker.ns = 'grassland_nipun_mines'
            marker.id = idx * 2
            marker.type = Marker.CYLINDER
            marker.action = Marker.ADD
            marker.pose.position.x = float(m['x'])
            marker.pose.position.y = float(m['y'])
            marker.pose.position.z = float(m['z']) + 0.05
            marker.pose.orientation.w = 1.0
            marker.scale.x = 0.20
            marker.scale.y = 0.20
            marker.scale.z = 0.08

            is_wf = "WF" in m['name']
            if is_wf:
                # Golden yellow for W-formation stations
                marker.color.r = 0.95
                marker.color.g = 0.75
                marker.color.b = 0.10
                marker.color.a = 0.85
            else:
                # Emerald green for perimeter floral field stations
                marker.color.r = 0.15
                marker.color.g = 0.80
                marker.color.b = 0.40
                marker.color.a = 0.75

            marker_array.markers.append(marker)

            # Text Label Marker
            txt = Marker()
            txt.header.stamp = now
            txt.header.frame_id = 'odom'
            txt.ns = 'grassland_nipun_labels'
            txt.id = idx * 2 + 1
            txt.type = Marker.TEXT_VIEW_FACING
            txt.action = Marker.ADD
            txt.pose.position.x = float(m['x'])
            txt.pose.position.y = float(m['y'])
            txt.pose.position.z = float(m['z']) + 0.35
            txt.pose.orientation.w = 1.0
            txt.scale.z = 0.22
            txt.text = f"{m['name']} ({m['x']:.1f}, {m['y']:.1f})"
            txt.color.r = 1.0
            txt.color.g = 1.0
            txt.color.b = 1.0
            txt.color.a = 0.90
            marker_array.markers.append(txt)

        self.marker_pub.publish(marker_array)

        # 3. Status string
        status_msg = String()
        status_msg.data = f"ALPINE_GRASSLAND_MINEFIELD: {len(self.mines)} NIPUN AP Stations Registered | Robot: ({self.robot_x:.2f}, {self.robot_y:.2f})"
        self.status_pub.publish(status_msg)


def main(args=None):
    rclpy.init(args=args)
    node = GrasslandMineTrackerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
