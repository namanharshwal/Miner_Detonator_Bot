#!/usr/bin/env python3
"""
Interactive All-Terrain AMR Teleoperation & Tactical Mine Defusal Controller
"""
import sys
import select
import termios
import tty
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String

HELP_MSG = """
================================================================================
🎖️  ALL-TERRAIN AMR TELEOPERATION & TACTICAL DEFUSAL CONSOLE
================================================================================
[Navigation Controls]
       w
   a   s   d
       x

   w/s : Increase/Decrease linear velocity (forward/reverse)
   a/d : Increase/Decrease angular velocity (steer left/right)
   space / x : Emergency Stop (halt all wheels)

[Tactical Mine Defusal Practices]
   1   : Switch Practice to LASER THERMAL (Standoff optical neutralization)
   2   : Switch Practice to RF DETONATOR JAMMING (Frequency inhibit field)
   3   : Switch Practice to MECHANICAL PIN-LOCK (Robotic extractor probe)
   4   : Switch Practice to CHEMICAL FOAM (Polymer explosive inhibitor)
   5   : Switch Practice to AUTO (Adaptive threat selection)
   f / t : FIRE / TRIGGER defusal sequence on nearest detected mine
   m   : Toggle Autonomous Proximity Defusal (ON/OFF)

CTRL-C to exit
================================================================================
"""

class AMRTeleopNode(Node):
    def __init__(self):
        super().__init__('amr_teleop_keyboard')
        self.vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.cmd_pub = self.create_publisher(String, '/army_mine_amr/defuse_cmd', 10)

        self.linear_speed = 0.5
        self.angular_speed = 1.0
        self.linear_step = 0.1
        self.angular_step = 0.2

        self.cur_linear = 0.0
        self.cur_angular = 0.0
        self.auto_enabled = True

    def get_key(self, settings):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        return key

    def run(self):
        settings = termios.tcgetattr(sys.stdin)
        print(HELP_MSG)

        try:
            while rclpy.ok():
                key = self.get_key(settings)
                if not key:
                    continue

                if key == '\x03': # Ctrl-C
                    break
                elif key == 'w':
                    self.cur_linear = min(self.cur_linear + self.linear_step, 1.5)
                elif key == 's':
                    self.cur_linear = max(self.cur_linear - self.linear_step, -1.5)
                elif key == 'a':
                    self.cur_angular = min(self.cur_angular + self.angular_step, 2.5)
                elif key == 'd':
                    self.cur_angular = max(self.cur_angular - self.angular_step, -2.5)
                elif key in [' ', 'x']:
                    self.cur_linear = 0.0
                    self.cur_angular = 0.0
                    print("🛑 EMERGENCY STOP")
                elif key == '1':
                    self.send_defuse_cmd('laser')
                elif key == '2':
                    self.send_defuse_cmd('rf_jam')
                elif key == '3':
                    self.send_defuse_cmd('mechanical')
                elif key == '4':
                    self.send_defuse_cmd('chemical')
                elif key == '5':
                    self.send_defuse_cmd('auto')
                elif key in ['f', 't']:
                    self.send_defuse_cmd('trigger')
                elif key == 'm':
                    self.auto_enabled = not self.auto_enabled
                    cmd = 'enable_auto' if self.auto_enabled else 'disable_auto'
                    self.send_defuse_cmd(cmd)

                twist = Twist()
                twist.linear.x = self.cur_linear
                twist.angular.z = self.cur_angular
                self.vel_pub.publish(twist)

                sys.stdout.write(f"\r🚀 Speed: Linear={self.cur_linear:.2f} m/s | Angular={self.cur_angular:.2f} rad/s    ")
                sys.stdout.flush()

        finally:
            twist = Twist()
            self.vel_pub.publish(twist)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

    def send_defuse_cmd(self, cmd_str):
        msg = String()
        msg.data = cmd_str
        self.cmd_pub.publish(msg)
        print(f"\n📡 Sent Defusal Command: [{cmd_str.upper()}]")

def main(args=None):
    rclpy.init(args=args)
    node = AMRTeleopNode()
    try:
        node.run()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
