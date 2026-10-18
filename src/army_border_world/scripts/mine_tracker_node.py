#!/usr/bin/env python3
"""
Army Border Mine Tracker & Defusal ROS 2 Node
Tracks bomb mines across the uneven border terrain, publishes coordinates and RViz markers,
and handles mine defusal triggers from mobile robot navigation.
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

class MineTrackerNode(Node):
    def __init__(self):
        super().__init__('mine_tracker_node')

        # Load mines config
        try:
            pkg_share = get_package_share_directory('army_border_world')
            config_path = os.path.join(pkg_share, 'config', 'mine_field_coordinates.yaml')
        except Exception:
            # Fallback to local source path if running before install
            config_path = '/home/nammy/army_mine_bot/src/army_border_world/config/mine_field_coordinates.yaml'

        self.get_logger().info(f'Loading mine field config from: {config_path}')
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
            self.mines = data.get('mines', [])

        self.get_logger().info(f'Initialized with {len(self.mines)} bomb mines in border minefield.')

        # Robot pose tracking
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_z = 0.0
        self.robot_pose_received = False

        # Publishers
        self.pose_pub = self.create_publisher(PoseArray, '/army_mine_world/mines', 10)
        self.marker_pub = self.create_publisher(MarkerArray, '/army_mine_world/markers', 10)
        self.status_pub = self.create_publisher(String, '/army_mine_world/status', 10)

        # Subscribers
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        # Services
        self.defuse_srv = self.create_service(Trigger, '/army_mine_world/defuse_mine', self.defuse_service_callback)

        # Periodic timer (2 Hz)
        self.timer = self.create_timer(0.5, self.publish_mines)

    def odom_callback(self, msg: Odometry):
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y
        self.robot_z = msg.pose.pose.position.z
        self.robot_pose_received = True

        # Check proximity auto-defusal (e.g. within 0.75m radius)
        for m in self.mines:
            if not m.get('defused', False):
                dist = math.sqrt((m['x'] - self.robot_x)**2 + (m['y'] - self.robot_y)**2)
                if dist < 0.75:
                    m['defused'] = True
                    m['status'] = 'defused'
                    self.get_logger().info(f"💣 MINESWEEPER ALERT: Bomb mine [{m['id']}] ({m['type']}) successfully DEFUSED by mobile robot at distance {dist:.2f}m!")

    def defuse_service_callback(self, request, response):
        # Find nearest mine to robot or defuse next armed mine
        armed_mines = [m for m in self.mines if not m.get('defused', False)]
        if not armed_mines:
            response.success = True
            response.message = "All bomb mines are already defused! Area is secure."
            return response

        if self.robot_pose_received:
            # Defuse nearest
            armed_mines.sort(key=lambda m: math.sqrt((m['x'] - self.robot_x)**2 + (m['y'] - self.robot_y)**2))
            target = armed_mines[0]
            dist = math.sqrt((target['x'] - self.robot_x)**2 + (target['y'] - self.robot_y)**2)
            target['defused'] = True
            target['status'] = 'defused'
            response.success = True
            response.message = f"Defused nearest mine [{target['id']}] at distance {dist:.2f}m."
        else:
            target = armed_mines[0]
            target['defused'] = True
            target['status'] = 'defused'
            response.success = True
            response.message = f"Manually defused mine [{target['id']}]."

        return response

    def publish_mines(self):
        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        header.frame_id = 'odom'
        spawn_offset_x = 5.5  # robot spawned at x = -5.5 in world

        # 1. PoseArray
        pose_array = PoseArray()
        pose_array.header = header

        marker_array = MarkerArray()
        defused_count = 0

        for idx, m in enumerate(self.mines):
            is_defused = m.get('defused', False)
            if is_defused:
                defused_count += 1

            # Pose in odom frame
            ox = float(m['x']) + spawn_offset_x
            oy = float(m['y'])
            oz = float(m['z'])

            p = Pose()
            p.position.x = ox
            p.position.y = oy
            p.position.z = oz
            pose_array.poses.append(p)

            # Visual marker (Disc/cylinder)
            marker = Marker()
            marker.header = header
            marker.ns = 'mines'
            marker.id = idx * 2
            marker.type = Marker.CYLINDER
            marker.action = Marker.ADD
            marker.pose.position.x = ox
            marker.pose.position.y = oy
            marker.pose.position.z = oz + 0.05
            marker.pose.orientation.w = 1.0

            if m['type'] == 'anti_tank':
                marker.scale.x = 0.35
                marker.scale.y = 0.35
                marker.scale.z = 0.10
            else:
                marker.scale.x = 0.20
                marker.scale.y = 0.20
                marker.scale.z = 0.08

            if is_defused:
                # Green for defused
                marker.color.r = 0.1
                marker.color.g = 0.9
                marker.color.b = 0.1
                marker.color.a = 0.8
            else:
                # Bright red for live armed bomb mine
                marker.color.r = 0.95
                marker.color.g = 0.1
                marker.color.b = 0.1
                marker.color.a = 0.9

            marker_array.markers.append(marker)

            # Text marker with Mine ID
            text_marker = Marker()
            text_marker.header = header
            text_marker.ns = 'mine_labels'
            text_marker.id = idx * 2 + 1
            text_marker.type = Marker.TEXT_VIEW_FACING
            text_marker.action = Marker.ADD
            text_marker.pose.position.x = ox
            text_marker.pose.position.y = oy
            text_marker.pose.position.z = oz + 0.35
            text_marker.scale.z = 0.15
            status_tag = "DEFUSED" if is_defused else "LIVE MINE"
            text_marker.text = f"{m['id']}\n[{status_tag}]"
            text_marker.color.r = 1.0 if not is_defused else 0.2
            text_marker.color.g = 0.2 if not is_defused else 1.0
            text_marker.color.b = 0.2
            text_marker.color.a = 1.0
            marker_array.markers.append(text_marker)

        self.pose_pub.publish(pose_array)
        self.marker_pub.publish(marker_array)

        # Status summary
        status_msg = String()
        total = len(self.mines)
        armed = total - defused_count
        status_msg.data = f"Minefield Status: Total={total} | Armed={armed} | Defused={defused_count}"
        self.status_pub.publish(status_msg)

def main(args=None):
    rclpy.init(args=args)
    node = MineTrackerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
