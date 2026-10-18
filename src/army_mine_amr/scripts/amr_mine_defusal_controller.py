#!/usr/bin/env python3
"""
================================================================================
ARMY BORDER MINE DEFUSAL CONTROLLER FOR ALL-TERRAIN AMR
================================================================================
Implements 4 distinct mine neutralization practices:
  1. LASER_THERMAL: Focused high-energy optical neutralization (Standoff: 1.8m)
  2. RF_JAMMING: Multi-band wireless & anti-handling detonator inhibitor (Range: 2.2m)
  3. MECHANICAL_PIN: Precision mechanical safety pin lockout probe (Range: 0.9m)
  4. CHEMICAL_FOAM: Catalytic neutralizing polymer foam spray (Range: 1.2m)

Features:
- Proximity detection using robot odometry on uneven terrain
- Real-time RViz 3D visual effects (targeting laser beam, RF pulse field, disarm rings)
- Integration with /army_mine_world/defuse_mine service
- Auto-Defusal and Manual practice command triggers
================================================================================
"""

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseArray, Point
from nav_msgs.msg import Odometry
from std_msgs.msg import String, Header, ColorRGBA
from std_srvs.srv import Trigger
from visualization_msgs.msg import Marker, MarkerArray

PRACTICE_RANGES = {
    'laser': 1.8,
    'rf_jam': 2.2,
    'mechanical': 0.9,
    'chemical': 1.2
}

PRACTICE_COLORS = {
    'laser': (1.0, 0.1, 0.1),        # Bright Red beam
    'rf_jam': (0.1, 0.7, 1.0),       # Cyan EM bubble
    'mechanical': (1.0, 0.8, 0.0),    # Amber mechanical lock
    'chemical': (0.2, 0.9, 0.3)       # Toxic green foam
}

class AMRDefusalController(Node):
    def __init__(self):
        super().__init__('amr_mine_defusal_controller')

        # Robot State
        self.rx = 0.0
        self.ry = 0.0
        self.rz = 0.0
        self.odom_received = False

        # Current practice mode ('auto', 'laser', 'rf_jam', 'mechanical', 'chemical')
        self.active_practice = 'auto'
        self.auto_defuse_enabled = True

        # Mines cache
        self.mines = []
        self.defused_mines = set()

        # Defusal animation state
        self.active_effects = []

        # ROS Publishers
        self.status_pub = self.create_publisher(String, '/army_mine_amr/defusal_status', 10)
        self.effects_pub = self.create_publisher(MarkerArray, '/army_mine_amr/markers', 10)

        # ROS Subscribers
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_cb, 10)
        self.mines_sub = self.create_subscription(PoseArray, '/army_mine_world/mines', self.mines_cb, 10)
        self.cmd_sub = self.create_subscription(String, '/army_mine_amr/defuse_cmd', self.cmd_cb, 10)

        # Service Client to World Defusal Service
        self.defuse_cli = self.create_client(Trigger, '/army_mine_world/defuse_mine')

        # Control Loop (5 Hz)
        self.timer = self.create_timer(0.2, self.control_loop)
        self.get_logger().info("🎖️  AMR Mine Defusal Controller initialized with 4 Neutralization Practices.")

    def odom_cb(self, msg: Odometry):
        self.rx = msg.pose.pose.position.x
        self.ry = msg.pose.pose.position.y
        self.rz = msg.pose.pose.position.z
        self.odom_received = True

    def mines_cb(self, msg: PoseArray):
        # Update mines list from world
        new_mines = []
        for idx, p in enumerate(msg.poses):
            m_id = f"mine_{idx+1:02d}"
            new_mines.append({
                'id': m_id,
                'x': p.position.x,
                'y': p.position.y,
                'z': p.position.z
            })
        self.mines = new_mines

    def cmd_cb(self, msg: String):
        cmd = msg.data.strip().lower()
        if cmd in ['laser', 'rf_jam', 'mechanical', 'chemical', 'auto']:
            self.active_practice = cmd
            self.get_logger().info(f"⚙️ Defusal practice switched to: [{self.active_practice.upper()}]")
        elif cmd == 'trigger':
            self.trigger_manual_defuse()
        elif cmd == 'enable_auto':
            self.auto_defuse_enabled = True
            self.get_logger().info("🤖 Autonomous proximity defusal ENABLED.")
        elif cmd == 'disable_auto':
            self.auto_defuse_enabled = False
            self.get_logger().info("🛑 Autonomous proximity defusal DISABLED (Manual only).")

    def control_loop(self):
        if not self.odom_received or not self.mines:
            return

        nearest_mine = None
        min_dist = float('inf')

        for m in self.mines:
            if m['id'] in self.defused_mines:
                continue
            d = math.sqrt((m['x'] - self.rx)**2 + (m['y'] - self.ry)**2)
            if d < min_dist:
                min_dist = d
                nearest_mine = m

        # Publish status
        status_text = (
            f"Robot: ({self.rx:.2f}, {self.ry:.2f}) | "
            f"Practice: {self.active_practice.upper()} | "
            f"Defused: {len(self.defused_mines)}/{len(self.mines)} | "
        )
        if nearest_mine:
            status_text += f"Nearest: [{nearest_mine['id']}] at {min_dist:.2f}m"
        else:
            status_text += "ALL MINES DEFUSED! Area Secure."
        
        stat_msg = String()
        stat_msg.data = status_text
        self.status_pub.publish(stat_msg)

        # Check proximity defusal
        if nearest_mine and self.auto_defuse_enabled:
            # Determine practice to use
            practice = self.select_practice(nearest_mine, min_dist)
            effective_range = PRACTICE_RANGES[practice]

            if min_dist <= effective_range:
                self.execute_defuse(nearest_mine, practice, min_dist)

        # Publish visual effects markers
        self.publish_effects()

    def select_practice(self, mine, dist):
        if self.active_practice != 'auto':
            return self.active_practice
        
        # Auto-selection logic:
        # Distance > 1.5m -> RF Jamming or Laser
        # Distance < 1.0m -> Mechanical probe
        # Mid distance -> Chemical foam
        if dist > 1.5:
            return 'rf_jam'
        elif dist > 1.0:
            return 'laser'
        else:
            return 'mechanical'

    def execute_defuse(self, mine, practice, dist):
        m_id = mine['id']
        self.defused_mines.add(m_id)

        self.get_logger().info(
            f"💥 [DEFUSAL SUCCESS] Disarmed [{m_id}] using [{practice.upper()}] practice at distance {dist:.2f}m!"
        )

        # Trigger world defusal service
        if self.defuse_cli.wait_for_service(timeout_sec=0.2):
            req = Trigger.Request()
            self.defuse_cli.call_async(req)

        # Add visual effect
        self.active_effects.append({
            'mine': mine,
            'practice': practice,
            'time_left': 25 # cycles to display
        })

    def trigger_manual_defuse(self):
        # Defuse nearest mine within 2.5m
        if not self.mines:
            return
        candidates = [m for m in self.mines if m['id'] not in self.defused_mines]
        if not candidates:
            self.get_logger().info("All mines already defused!")
            return

        candidates.sort(key=lambda m: math.sqrt((m['x'] - self.rx)**2 + (m['y'] - self.ry)**2))
        target = candidates[0]
        dist = math.sqrt((target['x'] - self.rx)**2 + (target['y'] - self.ry)**2)
        practice = self.active_practice if self.active_practice != 'auto' else 'laser'

        if dist <= PRACTICE_RANGES[practice] + 0.5:
            self.execute_defuse(target, practice, dist)
        else:
            self.get_logger().warn(f"Target [{target['id']}] too far ({dist:.2f}m) for practice [{practice}]. Move closer!")

    def publish_effects(self):
        ma = MarkerArray()
        now = self.get_clock().now().to_msg()

        # Update active effects
        surviving_effects = []
        for idx, eff in enumerate(self.active_effects):
            eff['time_left'] -= 1
            mine = eff['mine']
            practice = eff['practice']
            r, g, b = PRACTICE_COLORS[practice]

            # 1. Neutralization Effect Marker
            m1 = Marker()
            m1.header.frame_id = 'odom'
            m1.header.stamp = now
            m1.ns = 'defusal_effects'
            m1.id = idx * 2

            if practice == 'laser':
                # Line strip laser beam from robot probe to mine
                m1.type = Marker.LINE_STRIP
                m1.scale.x = 0.03 # Beam thickness
                m1.points = [
                    Point(x=self.rx, y=self.ry, z=self.rz + 0.08),
                    Point(x=mine['x'], y=mine['y'], z=mine['z'] + 0.04)
                ]
                m1.color = ColorRGBA(r=r, g=g, b=b, a=0.9)
            elif practice == 'rf_jam':
                # Expanding sphere field
                m1.type = Marker.SPHERE
                m1.pose.position.x = mine['x']
                m1.pose.position.y = mine['y']
                m1.pose.position.z = mine['z'] + 0.2
                m1.scale.x = 1.2
                m1.scale.y = 1.2
                m1.scale.z = 0.8
                m1.color = ColorRGBA(r=r, g=g, b=b, a=0.35)
            elif practice == 'mechanical':
                # Cylinder probe indicator
                m1.type = Marker.CYLINDER
                m1.pose.position.x = mine['x']
                m1.pose.position.y = mine['y']
                m1.pose.position.z = mine['z'] + 0.25
                m1.scale.x = 0.06
                m1.scale.y = 0.06
                m1.scale.z = 0.5
                m1.color = ColorRGBA(r=r, g=g, b=b, a=0.9)
            else: # chemical
                # Foam cloud
                m1.type = Marker.SPHERE
                m1.pose.position.x = mine['x']
                m1.pose.position.y = mine['y']
                m1.pose.position.z = mine['z'] + 0.1
                m1.scale.x = 0.8
                m1.scale.y = 0.8
                m1.scale.z = 0.3
                m1.color = ColorRGBA(r=r, g=g, b=b, a=0.6)

            ma.markers.append(m1)

            # 2. Defused Green Ring Badge
            m2 = Marker()
            m2.header.frame_id = 'odom'
            m2.header.stamp = now
            m2.ns = 'defused_badges'
            m2.id = idx * 2 + 1
            m2.type = Marker.CYLINDER
            m2.pose.position.x = mine['x']
            m2.pose.position.y = mine['y']
            m2.pose.position.z = mine['z'] + 0.02
            m2.scale.x = 0.65
            m2.scale.y = 0.65
            m2.scale.z = 0.02
            m2.color = ColorRGBA(r=0.0, g=1.0, b=0.2, a=0.8)
            ma.markers.append(m2)

            if eff['time_left'] > 0:
                surviving_effects.append(eff)

        self.active_effects = surviving_effects
        self.effects_pub.publish(ma)

def main(args=None):
    rclpy.init(args=args)
    node = AMRDefusalController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
