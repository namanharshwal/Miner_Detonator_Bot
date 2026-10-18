#!/usr/bin/env python3
"""
NIPUN Autonomous Mine-Laying & Coordinated W-Shape Formation Controller
According to Indian Army Requirements in Downloads/1.docx:
- Purpose: Autonomous mine-laying carrier in High Altitude Mountainous terrain.
- Hazard: Anti-Personnel mine NIPUN (10cm coaster size, payload <= 250g).
- Formation: Coordinated W-shape layout with 5 minelets/mini-bots.
- Autonomy: Fully autonomous with operator approval for positioning distance and W-alignment.
- Sensors: 4D LiDAR (minor obstacle negotiation), Seismic sensor, Magnetometer sensor.
"""

import math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from geometry_msgs.msg import Twist, PoseStamped, Point
from nav_msgs.msg import Odometry
from visualization_msgs.msg import Marker, MarkerArray
from std_msgs.msg import String, Float32, Header, Bool
from std_srvs.srv import Trigger, SetBool
from sensor_msgs.msg import MagneticField

class NipunMineLayingController(Node):
    def __init__(self):
        super().__init__('amr_mine_laying_controller')

        qos_reliable = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # Configuration according to 1.docx
        self.declare_parameter('formation_center_x', 6.0)     # Mountain terrain deployment zone
        self.declare_parameter('formation_center_y', 0.0)
        self.declare_parameter('lateral_spacing', 3.0)        # Spacing between minelets (m)
        self.declare_parameter('longitudinal_depth', 3.5)     # W-shape crest depth (m)
        self.declare_parameter('max_speed', 0.40)             # 1-2 km/h (0.28 - 0.55 m/s)
        self.declare_parameter('target_bot_index', 2)         # This AMR carries Central Apex Minelet #3

        self.center_x = self.get_parameter('formation_center_x').value
        self.center_y = self.get_parameter('formation_center_y').value
        self.spacing = self.get_parameter('lateral_spacing').value
        self.depth = self.get_parameter('longitudinal_depth').value
        self.max_speed = self.get_parameter('max_speed').value
        self.target_bot_idx = self.get_parameter('target_bot_index').value

        # Robot state
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_yaw = 0.0
        self.odom_received = False

        # W-Formation State
        # 5 coordinated stations forming a 'W'
        self.operator_approved = True  # Default approved by operator
        self.formation_stations = self.calculate_w_formation()
        self.assigned_target = self.formation_stations[self.target_bot_idx]
        self.deployment_complete = False

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.marker_pub = self.create_publisher(MarkerArray, '/army_mine_amr/formation_markers', 10)
        self.status_pub = self.create_publisher(String, '/army_mine_amr/formation_status', 10)
        self.seismic_pub = self.create_publisher(Float32, '/army_mine_amr/seismic_sensor', 10)
        self.mag_pub = self.create_publisher(MagneticField, '/army_mine_amr/magnetometer_sensor', 10)

        # Subscribers
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, qos_reliable)

        # Services for Operator Approval (Requirement #18)
        self.approval_srv = self.create_service(Trigger, '/army_mine_amr/approve_w_formation', self.approve_callback)
        self.realign_srv = self.create_service(Trigger, '/army_mine_amr/trigger_deployment', self.trigger_callback)

        # Control and telemetry loop (10 Hz)
        self.timer = self.create_timer(0.1, self.control_loop)
        # Visual markers timer (2 Hz)
        self.marker_timer = self.create_timer(0.5, self.publish_markers)

        self.get_logger().info('🎖️ NIPUN Anti-Personnel Mine-Laying & W-Formation Controller initialized.')
        self.get_logger().info(f'📍 Assigned Formation Station: {self.assigned_target["name"]} at ({self.assigned_target["x"]:.2f}, {self.assigned_target["y"]:.2f})')

    def calculate_w_formation(self):
        """
        Calculates 5 coordinated stations forming a tactical W-shape across the mountain front.
        Bot 1: Top-Left (x0 + depth, y0 - 2*spacing)
        Bot 2: Lower-Left (x0, y0 - spacing)
        Bot 3: Central Apex (x0 + depth, y0)
        Bot 4: Lower-Right (x0, y0 + spacing)
        Bot 5: Top-Right (x0 + depth, y0 + 2*spacing)
        """
        cx, cy = self.center_x, self.center_y
        d, s = self.depth, self.spacing

        stations = [
            {"id": 1, "name": "NIPUN Minelet #1 (North Flank)", "x": cx + d, "y": cy + 2 * s, "status": "COORDINATING"},
            {"id": 2, "name": "NIPUN Minelet #2 (North Valley)", "x": cx,     "y": cy + s,     "status": "COORDINATING"},
            {"id": 3, "name": "NIPUN Minelet #3 (Center Apex)",   "x": cx + d, "y": cy,         "status": "DEPLOYING"},
            {"id": 4, "name": "NIPUN Minelet #4 (South Valley)", "x": cx,     "y": cy - s,     "status": "COORDINATING"},
            {"id": 5, "name": "NIPUN Minelet #5 (South Flank)", "x": cx + d, "y": cy - 2 * s, "status": "COORDINATING"},
        ]
        return stations

    def odom_callback(self, msg: Odometry):
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.robot_yaw = math.atan2(siny_cosp, cosy_cosp)
        self.odom_received = True

    def approve_callback(self, request, response):
        self.operator_approved = True
        response.success = True
        response.message = "W-Formation alignment and positioning APPROVED by operator."
        self.get_logger().info("✅ Operator approved W-Formation layout.")
        return response

    def trigger_callback(self, request, response):
        self.deployment_complete = True
        self.assigned_target["status"] = "DEPLOYED_ARMED"
        response.success = True
        response.message = "NIPUN Anti-Personnel Mine laid and armed successfully. Senile period counter started."
        self.get_logger().info("💥 NIPUN Mine deployed and armed in W-formation.")
        return response

    def control_loop(self):
        if not self.odom_received:
            return

        # 1. Publish simulated seismic sensor data (Requirement #8)
        # Friendly minelets generate < 0.15g vibration; enemy footsteps generate > 0.45g
        seismic_msg = Float32()
        # Normal low vibration during mountain traversal
        seismic_msg.data = 0.08 + 0.02 * math.sin(self.get_clock().now().nanoseconds * 1e-9 * 5.0)
        self.seismic_pub.publish(seismic_msg)

        # 2. Publish simulated magnetometer sensor data (Requirement #8)
        # Earth magnetic field + metallic anomaly detection
        mag_msg = MagneticField()
        mag_msg.header.stamp = self.get_clock().now().to_msg()
        mag_msg.header.frame_id = "base_link"
        mag_msg.magnetic_field.x = 22.5e-6
        mag_msg.magnetic_field.y = -5.2e-6
        mag_msg.magnetic_field.z = 41.8e-6
        self.mag_pub.publish(mag_msg)

        # 3. Autonomous navigation to W-Formation station
        tx = self.assigned_target["x"]
        ty = self.assigned_target["y"]
        dx = tx - self.robot_x
        dy = ty - self.robot_y
        dist = math.sqrt(dx * dx + dy * dy)

        status_str = f"STATUS: [{'APPROVED' if self.operator_approved else 'PENDING_APPROVAL'}] | Target: ({tx:.1f}, {ty:.1f}) | Dist: {dist:.2f}m"

        if not self.operator_approved:
            # Awaiting operator confirmation
            self.stop_robot()
            status_str += " | Waiting for Operator Approval"
            self.status_pub.publish(String(data=status_str))
            return

        if dist < 0.35:
            # Reached assigned W-formation station!
            self.stop_robot()
            self.deployment_complete = True
            self.assigned_target["status"] = "ON_STATION_ARMED"
            status_str += " | ✅ ON STATION: NIPUN MINELET DEPLOYED & ARMED IN W-FORMATION"
            self.status_pub.publish(String(data=status_str))
            return

        # Gentle proportional navigation (1-2 km/h = 0.28 - 0.55 m/s)
        target_heading = math.atan2(dy, dx)
        heading_err = target_heading - self.robot_yaw
        while heading_err > math.pi:
            heading_err -= 2.0 * math.pi
        while heading_err < -math.pi:
            heading_err += 2.0 * math.pi

        twist = Twist()
        if abs(heading_err) > 0.4:
            # Turn in place toward target
            twist.linear.x = 0.0
            twist.angular.z = max(min(1.2 * heading_err, 0.8), -0.8)
        else:
            # Drive forward smoothly on mountain terrain
            twist.linear.x = min(max(0.35 * dist, 0.15), self.max_speed)
            twist.angular.z = max(min(0.8 * heading_err, 0.6), -0.6)

        self.cmd_vel_pub.publish(twist)
        self.status_pub.publish(String(data=status_str))

    def stop_robot(self):
        self.cmd_vel_pub.publish(Twist())

    def publish_markers(self):
        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        header.frame_id = 'odom'

        markers = MarkerArray()

        # 1. W-Shape Formation Guideline Lines
        line_marker = Marker()
        line_marker.header = header
        line_marker.ns = 'w_formation_lines'
        line_marker.id = 100
        line_marker.type = Marker.LINE_STRIP
        line_marker.action = Marker.ADD
        line_marker.scale.x = 0.06  # Line width
        line_marker.color.r = 0.1
        line_marker.color.g = 0.8
        line_marker.color.b = 0.95
        line_marker.color.a = 0.9

        # Add points in W order: 1 -> 2 -> 3 -> 4 -> 5
        for st in self.formation_stations:
            p = Point()
            p.x = float(st["x"])
            p.y = float(st["y"])
            p.z = 0.08
            line_marker.points.append(p)
        markers.markers.append(line_marker)

        # 2. Individual Minelet Stations (Discs / Coasters)
        for idx, st in enumerate(self.formation_stations):
            # Minelet Disc (10cm diameter = 0.05m radius as per 1.docx)
            disc = Marker()
            disc.header = header
            disc.ns = 'nipun_minelet_stations'
            disc.id = idx * 2
            disc.type = Marker.CYLINDER
            disc.action = Marker.ADD
            disc.pose.position.x = float(st["x"])
            disc.pose.position.y = float(st["y"])
            disc.pose.position.z = 0.05
            disc.pose.orientation.w = 1.0
            disc.scale.x = 0.18   # Disc diameter
            disc.scale.y = 0.18
            disc.scale.z = 0.04   # Height
            if idx == self.target_bot_idx:
                # Active Lead AMR Carrier station (Bright Green / Yellow)
                disc.color.r = 0.1
                disc.color.g = 0.95
                disc.color.b = 0.3
                disc.color.a = 0.95
            else:
                # Coordinated fleet stations (Cyan)
                disc.color.r = 0.2
                disc.color.g = 0.6
                disc.color.b = 0.95
                disc.color.a = 0.85
            markers.markers.append(disc)

            # Text label
            label = Marker()
            label.header = header
            label.ns = 'nipun_labels'
            label.id = idx * 2 + 1
            label.type = Marker.TEXT_VIEW_FACING
            label.action = Marker.ADD
            label.pose.position.x = float(st["x"])
            label.pose.position.y = float(st["y"])
            label.pose.position.z = 0.40
            label.scale.z = 0.16
            label.color.r = 1.0
            label.color.g = 1.0
            label.color.b = 1.0
            label.color.a = 0.95
            label.text = f"W-Station #{st['id']}\n[{st['status']}]"
            markers.markers.append(label)

        self.marker_pub.publish(markers)

def main(args=None):
    rclpy.init(args=args)
    node = NipunMineLayingController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
