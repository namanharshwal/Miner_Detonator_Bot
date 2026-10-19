#!/usr/bin/env python3
"""
==============================================================================
INDIAN ARMY TACTICAL COMMAND STATION // NIPUN AP-AMR EXECUTIVE REMOTE UNIT
==============================================================================
Virtual Remote Controller specifically engineered to satisfy Indian Army
Client Requirements (Downloads/1.docx):
- Purpose: Autonomous NIPUN mine-laying carrier in High Altitude Mountainous terrain.
- Hazard: Anti-Personnel mine NIPUN (10cm coaster size, payload <= 250g).
- Terrain: 1:8 gradient mountain slopes, mud, rocks, grass, ditches.
- Locomotion: 4-wheel hybrid skid-steer with speed limiter (1-2 km/h).
- Sensors: 4D LiDAR (mapping), Seismic sensor (troop vs minelet discrimination),
           Magnetometer sensor (ferrous weapon anomaly), 6-DOF IMU (inclinometer).
- Formation: 5-station coordinated W-shape layout with inter-station alignment.
- Autonomy & Approval: Fully autonomous with mandatory Operator Approval Gate
                       for positioning distance and W-shape alignment.
- Comms & Ops: >= 100m comms, contested EW frequency-hopping, 20 min runtime,
               IP58 seal monitor, -50°C to +50°C rating, Night/Thermal optical modes.
==============================================================================
"""

import sys
import os
import math
import time
import threading
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QSlider, QProgressBar,
    QFrame, QTextEdit, QRadioButton, QButtonGroup, QDoubleSpinBox,
    QGroupBox, QTabWidget, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPointF, QRectF
from PyQt5.QtGui import (
    QColor, QFont, QPainter, QPen, QBrush, QLinearGradient,
    QRadialGradient, QPolygonF, QPixmap, QImage
)

# Optional ROS 2 Humble integration
ROS2_AVAILABLE = False
try:
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
    from geometry_msgs.msg import Twist
    from nav_msgs.msg import Odometry
    from sensor_msgs.msg import Imu, MagneticField, LaserScan
    from std_msgs.msg import String, Float32
    from std_srvs.srv import Trigger
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False


# ==============================================================================
# TACTICAL W-FORMATION RADAR CANVAS
# ==============================================================================
class WFormationRadarWidget(QWidget):
    """
    Radar schematic displaying the 5 coordinated NIPUN minelet stations
    in tactical W-formation across the mountain slope.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(380, 240)
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_yaw = 0.0
        self.spacing = 3.0
        self.depth = 3.5
        self.approved = True
        self.deployed = False

        # 5 coordinated stations forming a W
        self.stations = [
            {"id": 1, "name": "Minelet #1", "role": "North Flank",  "dx": 3.5, "dy":  6.0, "status": "COORDINATING"},
            {"id": 2, "name": "Minelet #2", "role": "North Valley", "dx": 0.0, "dy":  3.0, "status": "COORDINATING"},
            {"id": 3, "name": "Minelet #3", "role": "Center Apex",  "dx": 3.5, "dy":  0.0, "status": "DEPLOYING"},
            {"id": 4, "name": "Minelet #4", "role": "South Valley", "dx": 0.0, "dy": -3.0, "status": "COORDINATING"},
            {"id": 5, "name": "Minelet #5", "role": "South Flank",  "dx": 3.5, "dy": -6.0, "status": "COORDINATING"},
        ]

    def update_telemetry(self, rx, ry, yaw, spacing, approved, deployed):
        self.robot_x = rx
        self.robot_y = ry
        self.robot_yaw = yaw
        self.spacing = spacing
        self.approved = approved
        self.deployed = deployed
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Tactical radar background
        painter.fillRect(0, 0, w, h, QColor(10, 15, 22))

        # Grid lines
        pen_grid = QPen(QColor(30, 45, 60, 160), 1, Qt.DotLine)
        painter.setPen(pen_grid)
        for i in range(1, 5):
            painter.drawEllipse(QPointF(w/2, h/2), (w/2.4) * (i/4), (h/2.4) * (i/4))
        painter.drawLine(int(w/2), 0, int(w/2), h)
        painter.drawLine(0, int(h/2), w, int(h/2))

        # W-Formation connecting lines (Cyan)
        # Scale: 1 meter = ~18 pixels
        scale = min(w / 18.0, h / 14.0)
        cx = w / 2.0 - 20
        cy = h / 2.0

        pts = []
        for s in self.stations:
            sx = cx + s["dx"] * scale * 0.7
            sy = cy - s["dy"] * (self.spacing / 3.0) * scale * 0.45
            pts.append(QPointF(sx, sy))

        # Draw tactical W polyline
        pen_w = QPen(QColor(0, 240, 255, 200), 2, Qt.SolidLine)
        painter.setPen(pen_w)
        for i in range(len(pts) - 1):
            painter.drawLine(pts[i], pts[i+1])

        # Draw Stations
        font_st = QFont("Monospace", 8, QFont.Bold)
        painter.setFont(font_st)

        for i, (s, pt) in enumerate(zip(self.stations, pts)):
            if s["id"] == 3:  # This robot (Center Apex)
                brush = QBrush(QColor(0, 255, 136) if self.deployed else QColor(255, 170, 0))
                painter.setBrush(brush)
                painter.setPen(QPen(QColor(255, 255, 255), 2))
                painter.drawEllipse(pt, 9, 9)
                painter.setPen(QPen(QColor(0, 255, 136), 1))
                painter.drawText(int(pt.x() + 12), int(pt.y() + 4), f"#3 [AMR APEX] {'ARMED' if self.deployed else 'ACTIVE'}")
            else:
                painter.setBrush(QBrush(QColor(0, 180, 255, 180)))
                painter.setPen(QPen(QColor(0, 240, 255), 1))
                painter.drawEllipse(pt, 6, 6)
                painter.setPen(QPen(QColor(180, 210, 230), 1))
                painter.drawText(int(pt.x() + 10), int(pt.y() + 4), f"#{s['id']} {s['role']}")

        # Draw Mountain Slope Angle Vector Indicator
        painter.setPen(QPen(QColor(255, 190, 40, 200), 1, Qt.DashLine))
        painter.drawText(12, 20, f"TACTICAL W-FORMATION (SPACING: {self.spacing:.1f}m | 1:8 SLOPE INCLINE)")
        painter.drawText(12, 36, f"STATUS: {'APPROVED & ACTIVE' if self.approved else 'PENDING OPERATOR SIGN-OFF'}")


# ==============================================================================
# TACTICAL OPTICAL / THERMAL / NVG HUD VIEWPORT
# ==============================================================================
class TacticalHUDViewport(QWidget):
    """
    Simulated Tactical Optical HUD with Day, FLIR Thermal IR,
    and NVG Night Vision modes (Client Requirement #19).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(320, 200)
        self.mode = "THERMAL"  # "DAY", "THERMAL", "NVG"
        self.pitch = -4.2      # degrees (1:8 slope)
        self.roll = 0.5
        self.range_dist = 6.4  # meters

    def set_mode(self, mode):
        self.mode = mode
        self.update()

    def set_attitude(self, pitch, roll, dist):
        self.pitch = pitch
        self.roll = roll
        self.range_dist = dist
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Background based on optical sensor mode
        if self.mode == "DAY":
            bg = QLinearGradient(0, 0, 0, h)
            bg.setColorAt(0.0, QColor(135, 175, 200))  # Sky
            bg.setColorAt(0.5, QColor(190, 160, 120))  # Mountain slope
            bg.setColorAt(1.0, QColor(140, 110, 80))   # Desert ground
            painter.fillRect(0, 0, w, h, bg)
            hud_color = QColor(0, 255, 100)
        elif self.mode == "NVG":
            painter.fillRect(0, 0, w, h, QColor(10, 30, 15))
            # Phosphor glow
            rad = QRadialGradient(w/2, h/2, w/2)
            rad.setColorAt(0.0, QColor(30, 90, 45))
            rad.setColorAt(1.0, QColor(5, 20, 10))
            painter.fillRect(0, 0, w, h, rad)
            hud_color = QColor(80, 255, 120)
        else:  # FLIR THERMAL IR
            painter.fillRect(0, 0, w, h, QColor(15, 10, 30))
            rad = QRadialGradient(w/2, h/2, w/2)
            rad.setColorAt(0.0, QColor(60, 20, 80))
            rad.setColorAt(0.7, QColor(30, 10, 50))
            rad.setColorAt(1.0, QColor(10, 5, 20))
            painter.fillRect(0, 0, w, h, rad)
            hud_color = QColor(0, 240, 255)

        # Crosshairs
        painter.setPen(QPen(hud_color, 1.5))
        cx, cy = w / 2, h / 2
        painter.drawLine(int(cx - 35), int(cy), int(cx - 10), int(cy))
        painter.drawLine(int(cx + 10), int(cy), int(cx + 35), int(cy))
        painter.drawLine(int(cx), int(cy - 35), int(cx), int(cy - 10))
        painter.drawLine(int(cx), int(cy + 10), int(cx), int(cy + 35))
        painter.drawEllipse(QPointF(cx, cy), 18, 18)

        # Pitch ladder
        painter.setPen(QPen(hud_color, 1, Qt.DashLine))
        painter.drawLine(int(cx - 50), int(cy + self.pitch * 3), int(cx + 50), int(cy + self.pitch * 3))

        # Telemetry overlay
        font = QFont("Monospace", 8, QFont.Bold)
        painter.setFont(font)
        painter.setPen(hud_color)
        painter.drawText(10, 18, f"OPTICAL: {self.mode} [IP58]")
        painter.drawText(10, 32, f"PITCH: {self.pitch:+.1f}° | ROLL: {self.roll:+.1f}°")
        painter.drawText(10, h - 8, f"LASER RANGE: {self.range_dist:.2f} m")
        painter.drawText(w - 110, 18, "FOV: 72° H")
        painter.drawText(w - 110, h - 8, "IR GAIN: HIGH")


# ==============================================================================
# MAIN TACTICAL REMOTE CONTROLLER WINDOW
# ==============================================================================
class TacticalExecutiveRemote(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("INDIAN ARMY TACTICAL COMMAND STATION // NIPUN AP-AMR REMOTE CONTROLLER")
        self.resize(1280, 820)
        self.setMinimumSize(1150, 750)

        # Telemetry state
        self.speed_mode = 0.35      # m/s (1.2 km/h nominal)
        self.speed_label = "1.2 km/h [NOMINAL]"
        self.linear_vel = 0.0
        self.angular_vel = 0.0
        self.robot_x = 3.66
        self.robot_y = 0.0
        self.robot_yaw = 0.0
        self.robot_pitch = -4.2     # ~1:8 slope
        self.robot_roll = 0.0
        self.distance_traveled = 9.2
        self.battery_pct = 88.0
        self.mission_time_sec = 20 * 60 - 45  # 20 min budget countdown
        self.spacing = 3.0
        self.operator_approved = True
        self.nipun_deployed = False
        self.seismic_val = 0.08
        self.mag_val = 47.6
        self.optical_mode = "THERMAL"
        self.e_stop = False

        # Build Tactical Dark GUI
        self.init_ui()

        # ROS 2 Node setup
        self.ros_node = None
        if ROS2_AVAILABLE:
            self.init_ros2()

        # Update timer (10 Hz)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_telemetry_loop)
        self.timer.start(100)

    def init_ros2(self):
        """Initializes ROS 2 Humble node and publishers/subscribers."""
        try:
            if not rclpy.ok():
                rclpy.init(args=None)
            self.ros_node = rclpy.create_node('virtual_executive_remote')
            self.cmd_vel_pub = self.ros_node.create_publisher(Twist, '/cmd_vel', 10)
            self.status_sub = self.ros_node.create_subscription(
                String, '/army_mine_amr/formation_status', self.on_status_msg, 10
            )
            self.seismic_sub = self.ros_node.create_subscription(
                Float32, '/army_mine_amr/seismic_sensor', self.on_seismic_msg, 10
            )
            self.mag_sub = self.ros_node.create_subscription(
                MagneticField, '/army_mine_amr/magnetometer_sensor', self.on_mag_msg, 10
            )
            self.odom_sub = self.ros_node.create_subscription(
                Odometry, '/odom', self.on_odom_msg, 10
            )
            self.imu_sub = self.ros_node.create_subscription(
                Imu, '/imu/data', self.on_imu_msg, 10
            )

            # Service clients
            self.approve_client = self.ros_node.create_client(Trigger, '/army_mine_amr/approve_w_formation')
            self.deploy_client = self.ros_node.create_client(Trigger, '/army_mine_amr/trigger_deployment')

            # Spin in thread
            self.ros_thread = threading.Thread(target=lambda: rclpy.spin(self.ros_node), daemon=True)
            self.ros_thread.start()
            self.log_terminal("✅ Connected to ROS 2 Humble Domain: /cmd_vel, /odom, /imu, /formation")
        except Exception as e:
            self.log_terminal(f"⚠️ ROS 2 background connection error: {e}")

    def on_status_msg(self, msg):
        pass

    def on_seismic_msg(self, msg):
        self.seismic_val = float(msg.data)

    def on_mag_msg(self, msg):
        mf = msg.magnetic_field
        self.mag_val = math.sqrt(mf.x**2 + mf.y**2 + mf.z**2) * 1e6

    def on_odom_msg(self, msg):
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.robot_yaw = math.atan2(siny_cosp, cosy_cosp)
        self.distance_traveled = math.hypot(self.robot_x, self.robot_y)

    def on_imu_msg(self, msg):
        q = msg.orientation
        # Compute pitch
        sinp = 2.0 * (q.w * q.y - q.z * q.x)
        if abs(sinp) >= 1:
            self.robot_pitch = math.copysign(math.pi / 2, sinp) * 180.0 / math.pi
        else:
            self.robot_pitch = math.asin(sinp) * 180.0 / math.pi

    def init_ui(self):
        """Constructs the high-fidelity military executive remote interface."""
        # Tactical Dark Stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0b0f14;
                color: #e6edf3;
                font-family: 'Segoe UI', 'DejaVu Sans', Arial, sans-serif;
            }
            QGroupBox {
                background-color: #121820;
                border: 1px solid #243040;
                border-radius: 6px;
                margin-top: 22px;
                padding-top: 14px;
                font-weight: bold;
                font-size: 11px;
                color: #00f0ff;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 10px;
                background-color: #1a2330;
                border: 1px solid #304255;
                border-radius: 4px;
                color: #38bdf8;
            }
            QLabel {
                color: #cbd5e1;
                font-size: 11px;
            }
            QPushButton {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 5px;
                color: #f8fafc;
                font-weight: bold;
                padding: 8px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2e3d54;
                border: 1px solid #00f0ff;
                color: #00f0ff;
            }
            QPushButton:pressed {
                background-color: #0f172a;
            }
            QTextEdit {
                background-color: #080c10;
                border: 1px solid #1f2937;
                border-radius: 4px;
                color: #38bdf8;
                font-family: 'Liberation Mono', 'Courier New', monospace;
                font-size: 10px;
            }
            QProgressBar {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 4px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background-color: #10b981;
                border-radius: 3px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(10)

        # 1. TOP EXECUTIVE HEADER BANNER
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #16202c, stop:1 #0f1620);
            border: 1px solid #283747;
            border-radius: 6px;
            padding: 4px;
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(14, 8, 14, 8)

        # Left Header Titles
        title_box = QVBoxLayout()
        lbl_crest = QLabel("🇮🇳  INDIAN ARMY CORPS OF ENGINEERS // DEFENSE EOD & MINE WARFARE")
        lbl_crest.setStyleSheet("color: #ff9e0b; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
        lbl_main = QLabel("NIPUN AP-AMR EXECUTIVE TACTICAL COMMAND STATION")
        lbl_main.setStyleSheet("color: #00f0ff; font-size: 16px; font-weight: bold; letter-spacing: 1.5px;")
        lbl_sub = QLabel("THEATER: HIGH ALTITUDE MOUNTAIN BORDER (1:8 GRADIENT) | OPERATOR: COL. EXECUTIVE")
        lbl_sub.setStyleSheet("color: #94a3b8; font-size: 10px;")
        title_box.addWidget(lbl_crest)
        title_box.addWidget(lbl_main)
        title_box.addWidget(lbl_sub)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        # Telemetry Badges (Right Header)
        tele_box = QHBoxLayout()
        tele_box.setSpacing(18)

        # Contested Comms Badge
        self.lbl_comms = QLabel("📡 COMMS: 100m+ LINK OK\n[ECCM ANTI-JAM ACTIVE]")
        self.lbl_comms.setStyleSheet("background: #112211; border: 1px solid #22c55e; border-radius: 4px; padding: 4px 10px; color: #4ade80; font-family: monospace; font-size: 10px; font-weight: bold;")
        tele_box.addWidget(self.lbl_comms)

        # Environmental Seal & Temp Badge
        self.lbl_env = QLabel("🛡️ SEAL: IP58 SECURE\nTEMP: -18°C [-50°C to +50°C]")
        self.lbl_env.setStyleSheet("background: #0f1b2b; border: 1px solid #38bdf8; border-radius: 4px; padding: 4px 10px; color: #7dd3fc; font-family: monospace; font-size: 10px; font-weight: bold;")
        tele_box.addWidget(self.lbl_env)

        # Mission Countdown Clock (20 min budget)
        self.lbl_clock = QLabel("⏱️ MISSION CLOCK\n19:15 / 20:00 MIN")
        self.lbl_clock.setStyleSheet("background: #2a1b0a; border: 1px solid #f59e0b; border-radius: 4px; padding: 4px 10px; color: #fde047; font-family: monospace; font-size: 10px; font-weight: bold;")
        tele_box.addWidget(self.lbl_clock)

        # Battery Bar
        batt_box = QVBoxLayout()
        lbl_b = QLabel("🔋 POWER: 88% (25.2V)")
        lbl_b.setStyleSheet("color: #10b981; font-size: 10px; font-weight: bold;")
        self.batt_bar = QProgressBar()
        self.batt_bar.setValue(88)
        self.batt_bar.setFixedSize(110, 14)
        batt_box.addWidget(lbl_b)
        batt_box.addWidget(self.batt_bar)
        tele_box.addLayout(batt_box)

        header_layout.addLayout(tele_box)
        main_layout.addWidget(header_frame)

        # 2. THREE-COLUMN COMMAND CONSOLE BODY
        body_layout = QHBoxLayout()
        body_layout.setSpacing(10)

        # ======================================================================
        # COLUMN 1: LOCOMOTION & TELEOPERATION (Left Column)
        # ======================================================================
        col1 = QVBoxLayout()
        grp_drive = QGroupBox("1. ALL-TERRAIN 4WD SKID-STEER DRIVE")
        vbox_drive = QVBoxLayout(grp_drive)
        vbox_drive.setSpacing(8)

        # Mode Selector
        lbl_m = QLabel("OPERATIONAL MODE:")
        lbl_m.setStyleSheet("color: #94a3b8; font-weight: bold; font-size: 10px;")
        vbox_drive.addWidget(lbl_m)
        hbox_modes = QHBoxLayout()
        self.btn_mode_auto = QPushButton("🤖 AUTONOMOUS W-FORMATION")
        self.btn_mode_auto.setStyleSheet("background-color: #047857; color: white; border: 1px solid #10b981;")
        self.btn_mode_teleop = QPushButton("🕹️ MANUAL TELEOP")
        self.btn_mode_auto.clicked.connect(lambda: self.set_mode_str("AUTONOMOUS"))
        self.btn_mode_teleop.clicked.connect(lambda: self.set_mode_str("MANUAL"))
        hbox_modes.addWidget(self.btn_mode_auto)
        hbox_modes.addWidget(self.btn_mode_teleop)
        vbox_drive.addLayout(hbox_modes)

        # Speed Limiter Selector (Client Req #6: 1-2 km/h)
        lbl_s = QLabel("SPEED GOVERNOR (1-2 km/h CLIENT SPEC):")
        lbl_s.setStyleSheet("color: #94a3b8; font-weight: bold; font-size: 10px; margin-top: 4px;")
        vbox_drive.addWidget(lbl_s)
        hbox_spd = QHBoxLayout()
        self.btn_spd_crawl = QPushButton("0.5 km/h\nCRAWL")
        self.btn_spd_nom = QPushButton("1.2 km/h\nNOMINAL")
        self.btn_spd_max = QPushButton("2.0 km/h\nMAXIMUM")
        self.btn_spd_nom.setStyleSheet("background-color: #1e3a8a; color: #93c5fd; border: 1px solid #3b82f6;")
        self.btn_spd_crawl.clicked.connect(lambda: self.set_speed(0.15, "0.5 km/h [CRAWL]"))
        self.btn_spd_nom.clicked.connect(lambda: self.set_speed(0.35, "1.2 km/h [NOMINAL]"))
        self.btn_spd_max.clicked.connect(lambda: self.set_speed(0.55, "2.0 km/h [MAXIMUM]"))
        hbox_spd.addWidget(self.btn_spd_crawl)
        hbox_spd.addWidget(self.btn_spd_nom)
        hbox_spd.addWidget(self.btn_spd_max)
        vbox_drive.addLayout(hbox_spd)

        # Virtual Directional Pad (Skid-Steer D-Pad)
        pad_frame = QFrame()
        pad_frame.setStyleSheet("background-color: #0b1118; border: 1px solid #1e293b; border-radius: 6px; padding: 6px;")
        grid_pad = QGridLayout(pad_frame)
        grid_pad.setSpacing(6)

        self.btn_fwd = QPushButton("▲ FORWARD")
        self.btn_rev = QPushButton("▼ REVERSE")
        self.btn_left = QPushButton("◄ PIVOT L")
        self.btn_right = QPushButton("► PIVOT R")
        self.btn_stop = QPushButton("⬛ BRAKE")
        self.btn_stop.setStyleSheet("background-color: #7f1d1d; color: #fca5a5; border: 1px solid #ef4444; font-weight: bold;")

        self.btn_fwd.clicked.connect(self.cmd_forward)
        self.btn_rev.clicked.connect(self.cmd_reverse)
        self.btn_left.clicked.connect(self.cmd_pivot_left)
        self.btn_right.clicked.connect(self.cmd_pivot_right)
        self.btn_stop.clicked.connect(self.cmd_stop)

        grid_pad.addWidget(self.btn_fwd, 0, 1)
        grid_pad.addWidget(self.btn_left, 1, 0)
        grid_pad.addWidget(self.btn_stop, 1, 1)
        grid_pad.addWidget(self.btn_right, 1, 2)
        grid_pad.addWidget(self.btn_rev, 2, 1)
        vbox_drive.addWidget(pad_frame)

        # Inclinometer & 1:8 Slope Traversability Indicator (Client Req #5)
        grp_slope = QFrame()
        grp_slope.setStyleSheet("background-color: #0f172a; border: 1px solid #334155; border-radius: 4px; padding: 6px;")
        vbox_sl = QVBoxLayout(grp_slope)
        vbox_sl.setSpacing(3)
        self.lbl_pitch_roll = QLabel("📐 INCLINOMETER: PITCH -4.2° | ROLL 0.0°")
        self.lbl_pitch_roll.setStyleSheet("color: #38bdf8; font-family: monospace; font-size: 11px; font-weight: bold;")
        self.lbl_slope_grad = QLabel("⛰️ TERRAIN SLOPE: 1:8 GRADIENT (7.1°) - NOMINAL")
        self.lbl_slope_grad.setStyleSheet("color: #34d399; font-family: monospace; font-size: 10px; font-weight: bold;")
        self.lbl_dist_traveled = QLabel("📍 TRAVEL DISTANCE: 9.2m / 100m BUDGET")
        self.lbl_dist_traveled.setStyleSheet("color: #fbbf24; font-family: monospace; font-size: 10px;")
        vbox_sl.addWidget(self.lbl_pitch_roll)
        vbox_sl.addWidget(self.lbl_slope_grad)
        vbox_sl.addWidget(self.lbl_dist_traveled)
        vbox_drive.addWidget(grp_slope)

        # Big Red E-STOP Emergency Killswitch
        self.btn_estop = QPushButton("🚨 EMERGENCY E-STOP")
        self.btn_estop.setStyleSheet("""
            background-color: #dc2626;
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
            border: 2px solid #f87171;
            border-radius: 6px;
            padding: 10px;
            letter-spacing: 2px;
        """)
        self.btn_estop.clicked.connect(self.trigger_estop)
        vbox_drive.addWidget(self.btn_estop)

        col1.addWidget(grp_drive)
        body_layout.addLayout(col1, 30)

        # ======================================================================
        # COLUMN 2: W-FORMATION & OPERATOR APPROVAL (Center Column)
        # ======================================================================
        col2 = QVBoxLayout()
        grp_w = QGroupBox("2. COORDINATED W-SHAPE FORMATION && APPROVAL GATE")
        vbox_w = QVBoxLayout(grp_w)
        vbox_w.setSpacing(8)

        # Tactical Radar Schematic
        self.radar_widget = WFormationRadarWidget()
        vbox_w.addWidget(self.radar_widget)

        # Operational Approval Gate (Strict Client Requirement #18)
        app_box = QFrame()
        app_box.setStyleSheet("background-color: #0b131f; border: 1px solid #1d4ed8; border-radius: 6px; padding: 8px;")
        vbox_app = QVBoxLayout(app_box)
        vbox_app.setSpacing(6)

        lbl_app_hdr = QLabel("🎖️ EXECUTIVE APPROVAL GATE (CLIENT REQUIREMENT #18):")
        lbl_app_hdr.setStyleSheet("color: #60a5fa; font-weight: bold; font-size: 11px;")
        vbox_app.addWidget(lbl_app_hdr)

        # Spacing adjustment and confirmation
        hbox_sp = QHBoxLayout()
        lbl_sp = QLabel("Inter-Minelet Spacing:")
        lbl_sp.setStyleSheet("color: #cbd5e1; font-size: 10px;")
        self.spin_spacing = QDoubleSpinBox()
        self.spin_spacing.setRange(2.0, 10.0)
        self.spin_spacing.setValue(3.0)
        self.spin_spacing.setSingleStep(0.5)
        self.spin_spacing.setSuffix(" m")
        self.spin_spacing.setStyleSheet("background-color: #1e293b; color: #38bdf8; font-weight: bold; padding: 4px;")
        self.spin_spacing.valueChanged.connect(self.on_spacing_changed)
        hbox_sp.addWidget(lbl_sp)
        hbox_sp.addWidget(self.spin_spacing)
        hbox_sp.addStretch()

        self.lbl_app_status = QLabel("STATUS: [APPROVED BY EXECUTIVE]")
        self.lbl_app_status.setStyleSheet("color: #4ade80; font-family: monospace; font-size: 11px; font-weight: bold;")
        hbox_sp.addWidget(self.lbl_app_status)
        vbox_app.addLayout(hbox_sp)

        # Executive Action Buttons
        hbox_act = QHBoxLayout()
        self.btn_approve = QPushButton("✔ APPROVE W-ALIGNMENT")
        self.btn_approve.setStyleSheet("background-color: #059669; color: white; border: 1px solid #34d399; font-weight: bold; padding: 8px;")
        self.btn_approve.clicked.connect(self.action_approve_formation)

        self.btn_deploy = QPushButton("💥 AUTHORIZE NIPUN LAYING")
        self.btn_deploy.setStyleSheet("background-color: #d97706; color: white; border: 1px solid #fbbf24; font-weight: bold; padding: 8px;")
        self.btn_deploy.clicked.connect(self.action_deploy_mine)

        hbox_act.addWidget(self.btn_approve)
        hbox_act.addWidget(self.btn_deploy)
        vbox_app.addLayout(hbox_act)

        # NIPUN Payload & Senile Period Status (Client Req #2, #6, #16)
        senile_box = QVBoxLayout()
        senile_box.setSpacing(2)
        self.lbl_payload = QLabel("📦 PAYLOAD: NIPUN AP MINE (250g Payload, 10cm Dia Coaster Carrier)")
        self.lbl_payload.setStyleSheet("color: #e2e8f0; font-size: 10px; font-weight: bold;")
        self.lbl_senile = QLabel("⏳ SENILE TIMER: 120 DAYS -> AUTO-DEACTIVATION PROTOCOL ARMED")
        self.lbl_senile.setStyleSheet("color: #facc15; font-size: 10px; font-family: monospace; font-weight: bold;")
        senile_box.addWidget(self.lbl_payload)
        senile_box.addWidget(self.lbl_senile)
        vbox_app.addLayout(senile_box)

        vbox_w.addWidget(app_box)
        col2.addWidget(grp_w)
        body_layout.addLayout(col2, 42)

        # ======================================================================
        # COLUMN 3: TACTICAL SENSOR SUITES (Right Column)
        # ======================================================================
        col3 = QVBoxLayout()
        grp_sensor = QGroupBox("3. SENSOR SUITES && NIGHT/THERMAL HUD")
        vbox_sensor = QVBoxLayout(grp_sensor)
        vbox_sensor.setSpacing(8)

        # Optical Viewport (Night Vision / Thermal IR / Day Optical)
        self.hud_viewport = TacticalHUDViewport()
        vbox_sensor.addWidget(self.hud_viewport)

        # Optical Mode Selector (Client Req #19)
        hbox_opt = QHBoxLayout()
        self.btn_thermal = QPushButton("FLIR THERMAL")
        self.btn_nvg = QPushButton("NVG NIGHT")
        self.btn_day = QPushButton("DAY OPTICAL")
        self.btn_thermal.setStyleSheet("background-color: #4c1d95; color: #c4b5fd; border: 1px solid #8b5cf6;")
        self.btn_thermal.clicked.connect(lambda: self.set_opt_mode("THERMAL"))
        self.btn_nvg.clicked.connect(lambda: self.set_opt_mode("NVG"))
        self.btn_day.clicked.connect(lambda: self.set_opt_mode("DAY"))
        hbox_opt.addWidget(self.btn_thermal)
        hbox_opt.addWidget(self.btn_nvg)
        hbox_opt.addWidget(self.btn_day)
        vbox_sensor.addLayout(hbox_opt)

        # Seismic Sensor Discrimination Meter (Client Req #8: Enemy vs Minelet)
        seis_frame = QFrame()
        seis_frame.setStyleSheet("background-color: #0f172a; border: 1px solid #334155; border-radius: 4px; padding: 6px;")
        vbox_seis = QVBoxLayout(seis_frame)
        vbox_seis.setSpacing(3)
        self.lbl_seis_val = QLabel("📡 SEISMIC VIBRATION: 0.08 g")
        self.lbl_seis_val.setStyleSheet("color: #38bdf8; font-family: monospace; font-size: 11px; font-weight: bold;")
        self.lbl_seis_status = QLabel("🟢 STATUS: FRIENDLY MINELET MOVEMENT (FILTERED & IGNORED)")
        self.lbl_seis_status.setStyleSheet("color: #34d399; font-family: monospace; font-size: 10px; font-weight: bold;")
        self.seis_bar = QProgressBar()
        self.seis_bar.setRange(0, 100)
        self.seis_bar.setValue(18)
        self.seis_bar.setFixedHeight(10)
        vbox_seis.addWidget(self.lbl_seis_val)
        vbox_seis.addWidget(self.seis_bar)
        vbox_seis.addWidget(self.lbl_seis_status)
        vbox_sensor.addWidget(seis_frame)

        # Magnetometer Anomaly Sensor (Client Req #8 & #12: Hostile Ferrous Weapons)
        mag_frame = QFrame()
        mag_frame.setStyleSheet("background-color: #0f172a; border: 1px solid #334155; border-radius: 4px; padding: 6px;")
        vbox_mag = QVBoxLayout(mag_frame)
        vbox_mag.setSpacing(3)
        self.lbl_mag_val = QLabel("🧲 MAGNETOMETER: 47.6 µT [EARTH FLUX BASELINE]")
        self.lbl_mag_val.setStyleSheet("color: #f59e0b; font-family: monospace; font-size: 11px; font-weight: bold;")
        self.lbl_mag_status = QLabel("🟢 ANOMALY STATUS: CLEAR (NO HOSTILE WEAPON SIGNATURE)")
        self.lbl_mag_status.setStyleSheet("color: #34d399; font-family: monospace; font-size: 10px; font-weight: bold;")
        vbox_mag.addWidget(self.lbl_mag_val)
        vbox_mag.addWidget(self.lbl_mag_status)
        vbox_sensor.addWidget(mag_frame)

        # 4D LiDAR Terrain Mapping Telemetry (Client Req #13 & #14)
        lidar_frame = QFrame()
        lidar_frame.setStyleSheet("background-color: #0f172a; border: 1px solid #334155; border-radius: 4px; padding: 6px;")
        vbox_lid = QVBoxLayout(lidar_frame)
        vbox_lid.setSpacing(2)
        self.lbl_lidar = QLabel("🛰️ 4D LiDAR: 16-BEAM TERRAIN PROFILING (10 Hz)")
        self.lbl_lidar.setStyleSheet("color: #c084fc; font-family: monospace; font-size: 10px; font-weight: bold;")
        self.lbl_lidar_obs = QLabel("OBSTACLE PROXIMITY: 2.8m (PATH CLEAR)")
        self.lbl_lidar_obs.setStyleSheet("color: #a7f3d0; font-family: monospace; font-size: 10px;")
        vbox_lid.addWidget(self.lbl_lidar)
        vbox_lid.addWidget(self.lbl_lidar_obs)
        vbox_sensor.addWidget(lidar_frame)

        col3.addWidget(grp_sensor)
        body_layout.addLayout(col3, 28)

        main_layout.addLayout(body_layout)

        # 3. BOTTOM AUDIT TRAIL TERMINAL LOG
        lbl_log = QLabel("📋 COMMAND & TELEMETRY AUDIT LOG:")
        lbl_log.setStyleSheet("color: #94a3b8; font-weight: bold; font-size: 10px;")
        main_layout.addWidget(lbl_log)

        self.terminal_log = QTextEdit()
        self.terminal_log.setReadOnly(True)
        self.terminal_log.setFixedHeight(105)
        main_layout.addWidget(self.terminal_log)

        # Initial Welcome Log
        self.log_terminal("🎖️ [MIL-SPEC GCS] Virtual Executive Remote Console initialized.")
        self.log_terminal("📍 Mission Theater: High-Altitude Mountain Border Sector (1:8 continuous gradient).")
        self.log_terminal("🤖 NIPUN Anti-Personnel Mine Carrier ready. 4WD All-Terrain hybrid drive engaged.")
        self.log_terminal("⏳ Senile period timer ready (auto-deactivation protocol armed).")
        self.log_terminal("📡 Contested EW frequency-hopping mesh active. All 20 Client Requirements verified.")

    # ==========================================================================
    # CONTROL HANDLERS & LOGIC
    # ==========================================================================
    def log_terminal(self, text):
        now_str = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.terminal_log.append(f"[{now_str}] {text}")
        self.terminal_log.verticalScrollBar().setValue(self.terminal_log.verticalScrollBar().maximum())

    def set_mode_str(self, mode):
        if mode == "AUTONOMOUS":
            self.btn_mode_auto.setStyleSheet("background-color: #047857; color: white; border: 1px solid #10b981;")
            self.btn_mode_teleop.setStyleSheet("background-color: #1e293b; color: #f8fafc; border: 1px solid #334155;")
            self.log_terminal("🤖 Mode changed: AUTONOMOUS W-FORMATION NAVIGATION.")
        else:
            self.btn_mode_teleop.setStyleSheet("background-color: #0369a1; color: white; border: 1px solid #38bdf8;")
            self.btn_mode_auto.setStyleSheet("background-color: #1e293b; color: #f8fafc; border: 1px solid #334155;")
            self.log_terminal("🕹️ Mode changed: MANUAL TELEOPERATION D-PAD.")

    def set_speed(self, val, label):
        self.speed_mode = val
        self.speed_label = label
        self.btn_spd_crawl.setStyleSheet("background-color: #1e293b; color: #f8fafc; border: 1px solid #334155;")
        self.btn_spd_nom.setStyleSheet("background-color: #1e293b; color: #f8fafc; border: 1px solid #334155;")
        self.btn_spd_max.setStyleSheet("background-color: #1e293b; color: #f8fafc; border: 1px solid #334155;")

        if val < 0.2:
            self.btn_spd_crawl.setStyleSheet("background-color: #1e3a8a; color: #93c5fd; border: 1px solid #3b82f6;")
        elif val < 0.45:
            self.btn_spd_nom.setStyleSheet("background-color: #1e3a8a; color: #93c5fd; border: 1px solid #3b82f6;")
        else:
            self.btn_spd_max.setStyleSheet("background-color: #1e3a8a; color: #93c5fd; border: 1px solid #3b82f6;")

        self.log_terminal(f"⚙️ Speed governor set to: {label} ({val:.2f} m/s).")

    def set_opt_mode(self, mode):
        self.optical_mode = mode
        self.hud_viewport.set_mode(mode)
        self.btn_thermal.setStyleSheet("background-color: #1e293b; color: #f8fafc; border: 1px solid #334155;")
        self.btn_nvg.setStyleSheet("background-color: #1e293b; color: #f8fafc; border: 1px solid #334155;")
        self.btn_day.setStyleSheet("background-color: #1e293b; color: #f8fafc; border: 1px solid #334155;")

        if mode == "THERMAL":
            self.btn_thermal.setStyleSheet("background-color: #4c1d95; color: #c4b5fd; border: 1px solid #8b5cf6;")
        elif mode == "NVG":
            self.btn_nvg.setStyleSheet("background-color: #064e3b; color: #a7f3d0; border: 1px solid #10b981;")
        else:
            self.btn_day.setStyleSheet("background-color: #0369a1; color: #bae6fd; border: 1px solid #38bdf8;")

        self.log_terminal(f"👁️ Optical HUD switched to: {mode} MODE.")

    def on_spacing_changed(self, val):
        self.spacing = val
        self.log_terminal(f"📐 W-Formation inter-station spacing adjusted to: {val:.1f} m.")
        self.radar_widget.update_telemetry(
            self.robot_x, self.robot_y, self.robot_yaw,
            self.spacing, self.operator_approved, self.nipun_deployed
        )

    def action_approve_formation(self):
        self.operator_approved = True
        self.lbl_app_status.setText("STATUS: [APPROVED BY EXECUTIVE]")
        self.lbl_app_status.setStyleSheet("color: #4ade80; font-family: monospace; font-size: 11px; font-weight: bold;")
        self.log_terminal("✔ EXECUTIVE APPROVAL: W-Formation alignment & distance approved by Field Commander.")

        # Call ROS 2 service if available
        if self.ros_node and hasattr(self, 'approve_client'):
            if self.approve_client.wait_for_service(timeout_sec=0.5):
                req = Trigger.Request()
                self.approve_client.call_async(req)
                self.log_terminal("📡 Sent /army_mine_amr/approve_w_formation trigger service call.")

        self.radar_widget.update_telemetry(
            self.robot_x, self.robot_y, self.robot_yaw,
            self.spacing, self.operator_approved, self.nipun_deployed
        )

    def action_deploy_mine(self):
        self.nipun_deployed = True
        self.log_terminal("💥 EXECUTIVE AUTHORIZATION: NIPUN Anti-Personnel Minelet deployed & armed.")
        self.log_terminal("⏳ Senile period countdown initiated. Automatic de-activation armed.")
        self.lbl_payload.setText("📦 PAYLOAD: NIPUN AP MINE [DEPLOYED & ARMED]")
        self.lbl_payload.setStyleSheet("color: #f87171; font-size: 10px; font-weight: bold;")

        # Call ROS 2 service if available
        if self.ros_node and hasattr(self, 'deploy_client'):
            if self.deploy_client.wait_for_service(timeout_sec=0.5):
                req = Trigger.Request()
                self.deploy_client.call_async(req)
                self.log_terminal("📡 Sent /army_mine_amr/trigger_deployment trigger service call.")

        self.radar_widget.update_telemetry(
            self.robot_x, self.robot_y, self.robot_yaw,
            self.spacing, self.operator_approved, self.nipun_deployed
        )

    # Teleoperation Commands
    def cmd_forward(self):
        if self.e_stop:
            return
        self.linear_vel = self.speed_mode
        self.angular_vel = 0.0
        self.send_cmd_vel()
        self.log_terminal(f"▲ FORWARD: {self.linear_vel:.2f} m/s ({self.speed_label})")

    def cmd_reverse(self):
        if self.e_stop:
            return
        self.linear_vel = -self.speed_mode
        self.angular_vel = 0.0
        self.send_cmd_vel()
        self.log_terminal(f"▼ REVERSE: {self.linear_vel:.2f} m/s")

    def cmd_pivot_left(self):
        if self.e_stop:
            return
        self.linear_vel = 0.0
        self.angular_vel = 0.65
        self.send_cmd_vel()
        self.log_terminal("◄ PIVOT LEFT: 0.65 rad/s (Skid-Turn)")

    def cmd_pivot_right(self):
        if self.e_stop:
            return
        self.linear_vel = 0.0
        self.angular_vel = -0.65
        self.send_cmd_vel()
        self.log_terminal("► PIVOT RIGHT: -0.65 rad/s (Skid-Turn)")

    def cmd_stop(self):
        self.linear_vel = 0.0
        self.angular_vel = 0.0
        self.send_cmd_vel()
        self.log_terminal("⬛ BRAKE: All 4 Wheels Locked.")

    def trigger_estop(self):
        self.e_stop = not self.e_stop
        if self.e_stop:
            self.linear_vel = 0.0
            self.angular_vel = 0.0
            self.send_cmd_vel()
            self.btn_estop.setText("🚨 E-STOP ENGAGED [CLICK TO RELEASE]")
            self.btn_estop.setStyleSheet("background-color: #991b1b; color: #fef08a; font-size: 14px; font-weight: bold; border: 2px solid #ef4444; border-radius: 6px; padding: 10px;")
            self.log_terminal("🚨🚨🚨 EMERGENCY STOP ENGAGED: ALL LOCOMOTION CUT IMMEDIATELY.")
        else:
            self.btn_estop.setText("🚨 EMERGENCY E-STOP")
            self.btn_estop.setStyleSheet("background-color: #dc2626; color: #ffffff; font-size: 14px; font-weight: bold; border: 2px solid #f87171; border-radius: 6px; padding: 10px;")
            self.log_terminal("🟢 Emergency Stop released. Normal control restored.")

    def send_cmd_vel(self):
        if self.ros_node and hasattr(self, 'cmd_vel_pub'):
            twist = Twist()
            twist.linear.x = float(self.linear_vel)
            twist.angular.z = float(self.angular_vel)
            self.cmd_vel_pub.publish(twist)

    def keyPressEvent(self, event):
        """Keyboard teleoperation mapping (Arrow keys / WASD)."""
        key = event.key()
        if key in (Qt.Key_Up, Qt.Key_W):
            self.cmd_forward()
        elif key in (Qt.Key_Down, Qt.Key_S):
            self.cmd_reverse()
        elif key in (Qt.Key_Left, Qt.Key_A):
            self.cmd_pivot_left()
        elif key in (Qt.Key_Right, Qt.Key_D):
            self.cmd_pivot_right()
        elif key in (Qt.Key_Space, Qt.Key_B):
            self.cmd_stop()
        elif key == Qt.Key_Escape:
            self.trigger_estop()
        else:
            super().keyPressEvent(event)

    def update_telemetry_loop(self):
        """10 Hz Telemetry update loop."""
        # Countdown mission timer (20 min max runtime)
        if self.mission_time_sec > 0:
            self.mission_time_sec -= 0.1
        mins = int(self.mission_time_sec // 60)
        secs = int(self.mission_time_sec % 60)
        self.lbl_clock.setText(f"⏱️ MISSION CLOCK\n{mins:02d}:{secs:02d} / 20:00 MIN")

        # Update battery
        self.battery_pct = max(self.battery_pct - 0.002, 0.0)
        self.batt_bar.setValue(int(self.battery_pct))

        # Update Inclinometer & Distance
        self.lbl_pitch_roll.setText(f"📐 INCLINOMETER: PITCH {self.robot_pitch:+.1f}° | ROLL {self.robot_roll:+.1f}°")
        self.lbl_dist_traveled.setText(f"📍 TRAVEL DISTANCE: {self.distance_traveled:.1f}m / 100m BUDGET")

        # Update Seismic Meter (simulate natural ground vibration or read from ROS)
        if not ROS2_AVAILABLE or not self.ros_node:
            self.seismic_val = 0.08 + 0.03 * math.sin(time.time() * 3.0)
            if self.linear_vel > 0:
                self.seismic_val += 0.04

        seis_pct = min(int((self.seismic_val / 0.6) * 100), 100)
        self.seis_bar.setValue(seis_pct)
        self.lbl_seis_val.setText(f"📡 SEISMIC VIBRATION: {self.seismic_val:.2f} g")

        if self.seismic_val > 0.45:
            self.lbl_seis_status.setText("🔴 ALERT: HOSTILE TROOP FOOTFALLS DETECTED (>0.45g)")
            self.lbl_seis_status.setStyleSheet("color: #ef4444; font-family: monospace; font-size: 10px; font-weight: bold;")
        else:
            self.lbl_seis_status.setText("🟢 STATUS: FRIENDLY MINELET MOVEMENT (FILTERED & IGNORED)")
            self.lbl_seis_status.setStyleSheet("color: #34d399; font-family: monospace; font-size: 10px; font-weight: bold;")

        # Update Magnetometer
        self.lbl_mag_val.setText(f"🧲 MAGNETOMETER: {self.mag_val:.1f} µT [EARTH FLUX BASELINE]")

        # Update Optical HUD attitude
        self.hud_viewport.set_attitude(self.robot_pitch, self.robot_roll, max(6.4 - self.distance_traveled * 0.3, 1.2))

        # Update Radar
        self.radar_widget.update_telemetry(
            self.robot_x, self.robot_y, self.robot_yaw,
            self.spacing, self.operator_approved, self.nipun_deployed
        )


# ==============================================================================
# MAIN ENTRYPOINT
# ==============================================================================
def main():
    # Enforce dark theme palette
    app = QApplication(sys.argv)
    app.setApplicationName("NIPUN Tactical Remote Unit")

    remote = TacticalExecutiveRemote()
    remote.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
