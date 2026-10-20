# Mountain Grassland World (`mountain_grassland_world`)
### Realistic High-Altitude Alpine Mountain Meadow with Lush Grass, Wildflowers & NIPUN Minefield Simulation for ROS 2 & Gazebo Sim Harmonic

[![ROS 2](https://img.shields.io/badge/ROS%202-Humble%20Hawksbill-22314E?logo=ros&logoColor=white)](https://docs.ros.org/en/humble/)
[![Gazebo](https://img.shields.io/badge/Gazebo%20Sim-Harmonic%208.14-FF6F00?logo=gazebo&logoColor=white)](https://gazebosim.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](../../LICENSE)

---

## 📌 Package Overview

The `mountain_grassland_world` package provides a dedicated, photorealistic **High-Altitude Alpine Mountain Grassland & Wildflower** simulation environment for the autonomous **Miner Detonator Bot (AMR)**. 

Engineered strictly against the client requirements defined in `1.docx`, this package simulates the rugged mountainous terrain of border regions featuring:
* **Alpine Meadow Grass**: High-density perennial mountain turf and ryegrass clumps.
* **Himalayan Wildflowers**: Intersecting floral clusters including Himalayan blue poppies, alpine buttercups, and mountain daisies.
* **Mountain Terrain & Drainage Swales**: Continuous variable gradient slope strictly constrained to **$\le 1:8$ ($\sim 7.1^\circ$)** as per operational client specifications.
* **Granite Rock & Boulder Formations**: Natural obstacle hazards requiring real-time 4D LiDAR and RealSense RGB-D obstacle negotiation.
* **Himalayan Pine Trees & Border Outposts**: High-altitude conifer trees and fortified military outpost perimeters.
* **18 NIPUN Anti-Personnel Minelet Stations**: Sized strictly to compact coaster-style dimensions ($\sim 10\text{ cm}$ diameter $\times 4\text{ cm}$ height), complete with coordinated 5-node W-formation stations and tactical mine field arrays.

---

## 🖼️ Visual Showcase

### Full Simulation Verification & Telemetry Dashboard
The dashboard demonstrates end-to-end integration: Gazebo Sim Harmonic 8.14 rendering the alpine meadow, RViz2 visual sensor fusion (RealSense D435 dense point cloud, 16-beam 4D LiDAR, SLAM occupancy grid), and the Army Executive Virtual Remote Controller in RGB-D Depth mode.

![Mountain Grassland Verification Dashboard](../../docs/images/mountain_grassland_verification_dashboard.png)

### Key Views
| Alpine Meadow & Flora (Gazebo Sim) | RealSense 3D Perception & SLAM (RViz2) | Executive Remote Controller (RGB-D Mode) |
|:---:|:---:|:---:|
| ![Gazebo Meadow](../../docs/images/gazebo_mountain_grassland_meadow.png) | ![RViz Perception](../../docs/images/rviz_mountain_grassland_driving.png) | ![Remote Controller](../../docs/images/remote_mountain_grassland_driving.png) |

---

## 🏗️ Architecture & Package Assets

```
mountain_grassland_world/
├── CMakeLists.txt                       # Build script (ament_cmake, ament_cmake_python)
├── package.xml                          # ROS 2 package manifest
├── README.md                            # Package documentation
├── config/
│   └── grassland_mine_coordinates.yaml  # 18 Anti-Personnel NIPUN minelet coordinates
├── launch/
│   ├── mountain_grassland_world.launch.py     # Standalone Gazebo world launcher
│   ├── mountain_grassland_with_amr.launch.py  # Master full-stack launcher (World + AMR + SLAM + RViz)
│   └── view_grassland_mines_rviz.launch.py    # Standalone RViz2 minelet visualizer
├── materials/textures/                  # 2048x2048 & 1024x1024 Photorealistic PBR Textures
│   ├── alpine_grass_meadow.png          # High-density mountain turf & soil
│   ├── alpine_grass_meadow_normal.png   # Tangent-space grass blade & soil normal map
│   ├── alpine_grass_meadow_roughness.png# PBR roughness map
│   ├── mountain_rock_cliff.png          # Granite metamorphic rock with lichen & quartz
│   ├── mountain_rock_cliff_normal.png   # Deep granite fracture normal map
│   ├── mountain_rock_cliff_roughness.png
│   ├── alpine_pine_foliage.png          # Alpha-masked conifer needle boughs
│   ├── alpine_pine_bark.png             # Conifer trunk furrowed bark
│   ├── alpine_wildflower_poppy.png      # Himalayan blue poppy (Meconopsis)
│   ├── alpine_wildflower_buttercup.png  # Golden alpine buttercup (Ranunculus)
│   ├── alpine_wildflower_daisy.png      # Mountain chamomile daisy (Asteraceae)
│   ├── alpine_wildflower_gentian.png    # Royal purple alpine gentian
│   └── alpine_dwarf_rhododendron.png    # Mountain evergreen shrub with pink blooms
├── models/                              # Photorealistic 3D SDF Models with PBR Materials
│   ├── alpine_mountain_terrain/         # 110m x 90m continuous slope mesh (<= 1:8 gradient)
│   ├── alpine_mountain_peaks/           # 360-degree surrounding Himalayan mountain horizon ring
│   ├── alpine_pine_tree/                # High-fidelity 3D conifer pine tree with bark & needle boughs
│   ├── alpine_glacial_boulder/          # Photogrammetry-scanned large granite erratic boulder
│   ├── alpine_medium_boulder/           # Photogrammetry-scanned medium mountain boulder
│   ├── alpine_meadow_rock/              # Photogrammetry-scanned weathered field rock
│   ├── alpine_granite_rock_2/           # Photogrammetry-scanned fractured rock fragment
│   ├── alpine_talus_scree/              # Photogrammetry-scanned scree stone scatter
│   ├── alpine_wildflower_poppy/         # Volumetric Himalayan blue poppy bouquet with basal rosette
│   ├── alpine_wildflower_buttercup/     # Volumetric golden buttercup cluster
│   ├── alpine_wildflower_daisy/         # Volumetric mountain daisy bed
│   ├── alpine_wildflower_gentian/       # Volumetric purple gentian cluster
│   ├── alpine_dwarf_rhododendron/       # Volumetric dwarf mountain shrub dome
│   ├── alpine_grass_tussock/            # Volumetric tall fescue grass tuft
│   ├── alpine_grass_clump/              # Multi-blade ryegrass clump
│   ├── border_meadow_outpost/           # Fortified outpost shelter (camo canvas, sandbags, comms mast)
│   └── nipun_mine_marker/               # 10cm dia x 4cm coaster-sized NIPUN minelet with LED
├── rviz/
│   └── mountain_grassland_slam.rviz     # Tailored RViz2 layout with RealSense RGB-D & LiDAR
└── scripts/
    ├── install_photorealistic_assets.py # Configures photogrammetry rocks and conifer models
    ├── create_realistic_textures.py     # Generates 2048x2048 PBR albedo, normal & roughness textures
    ├── build_realistic_models_and_world.py # Master procedural terrain & world builder
    └── grassland_mine_tracker_node.py   # Publishes /mountain_grassland/markers & /mines
```

---

## 🚀 Launch Instructions

### 1. Master Simulation with AMR, Depth Camera & SLAM
To launch the complete alpine mountain world with the 4WD NIPUN AMR, RealSense D435 depth camera, 4D LiDAR, SLAM Toolbox, and RViz2:
```bash
# Using the workspace launcher:
./launch_world.sh grassland

# Or directly via ROS 2 launch:
ros2 launch mountain_grassland_world mountain_grassland_with_amr.launch.py
```

### 2. Standalone Alpine Environment Inspection
To inspect the environment and models in Gazebo Sim GUI without spawning the robot:
```bash
./launch_world.sh grassland_gui

# Or directly via ROS 2 launch:
ros2 launch mountain_grassland_world mountain_grassland_world.launch.py
```

### 3. Launching the Army Executive Virtual Remote Controller
To teleoperate the robot across the alpine meadow and monitor RealSense depth telemetry:
```bash
./launch_remote.sh
```

---

## 📡 Published ROS 2 Topics

| Topic | Type | Description |
|---|---|---|
| `/mountain_grassland/markers` | `visualization_msgs/msg/MarkerArray` | RViz2 visual markers for all 18 NIPUN minelet sites (including W-formation) |
| `/mountain_grassland/mines` | `geometry_msgs/msg/PoseArray` | Metric 3D poses of all registered mine stations |
| `/camera/image_raw` | `sensor_msgs/msg/Image` | Forward RealSense D435 optical RGB camera feed (640x480 @ 20 Hz) |
| `/camera/depth/image_raw` | `sensor_msgs/msg/Image` | Metric depth map stream (`32FC1`) |
| `/camera/depth/points` | `sensor_msgs/msg/PointCloud2` | Dense 3D point cloud of grass, flowers, boulders, and terrain |
| `/lidar4d/points_raw` | `sensor_msgs/msg/PointCloud2` | 16-beam 4D LiDAR terrain point cloud |
| `/scan` | `sensor_msgs/msg/LaserScan` | 2D horizontal planar laser scan for SLAM |
| `/map` | `nav_msgs/msg/OccupancyGrid` | Real-time SLAM occupancy grid map |
| `/odom` | `nav_msgs/msg/Odometry` | Wheel odometry fused with 4WD skid-steer kinematics |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Velocity command input (linear & angular) |

---

## ⚙️ Compliance with Operational Specification `1.docx`

* **Req #3 & #4 (Operational Environment & Terrain)**: Realized in a standalone high-altitude mountain world featuring alpine grass, wildflowers, rocks, boulders, and drainage ditches.
* **Req #5 (Max Slope Gradient $\le 1:8$)**: Terrain elevation gradients strictly engineered to nominal ratios $\le 1:8$ ($\sim 7.1^\circ$), verified by the onboard inclinometer and odometry tracking.
* **Req #6 & #10 (Coaster-Sized NIPUN Minelets)**: All 18 registered mine models match the exact $10\text{ cm}$ diameter coaster form factor with distinctive military markings.
* **Req #13, #14 & #20 (Terrain Mapping & Minor Obstacle Negotiation)**: Dual sensory integration (RealSense D435 + 4D LiDAR) provides real-time obstacle avoidance and continuous SLAM occupancy grid generation.
