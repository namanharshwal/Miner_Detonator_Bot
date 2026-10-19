#!/bin/bash
# ==============================================================================
# Army Border Minefield Environment Quick Launcher
# ==============================================================================
set -e

WORKSPACE_DIR="/home/nammy/army_mine_bot"
WORLD_PATH="$WORKSPACE_DIR/src/army_border_world/worlds/army_border_minefield.sdf"
MODELS_PATH="$WORKSPACE_DIR/src/army_border_world/models"

# Ensure clean state: kill any stale servers
pkill -9 -f "ign gazebo" 2>/dev/null || true
pkill -9 -f "ign-gazebo-server" 2>/dev/null || true
pkill -9 -f "gz sim" 2>/dev/null || true
pkill -9 -f "gz-sim-server" 2>/dev/null || true
pkill -9 -f "gz-gui" 2>/dev/null || true
pkill -9 -f "ign-gui" 2>/dev/null || true
pkill -9 -f "parameter_bridge" 2>/dev/null || true
pkill -9 -f "slam_toolbox" 2>/dev/null || true
pkill -9 -f "robot_state_publisher" 2>/dev/null || true
pkill -9 -f "rviz2" 2>/dev/null || true
pkill -9 -f "mine_tracker" 2>/dev/null || true
pkill -9 -f "amr_mine_defusal" 2>/dev/null || true

# Export isolated Gazebo transport partition and local loopback IP
export GZ_PARTITION=army_mine_bot
export IGN_PARTITION=army_mine_bot
export GZ_IP=127.0.0.1
export IGN_IP=127.0.0.1
export ROS_DOMAIN_ID=42

# Export Gazebo Resource Paths
export GZ_SIM_RESOURCE_PATH="$MODELS_PATH:$WORKSPACE_DIR/src:$GZ_SIM_RESOURCE_PATH"
export IGN_GAZEBO_RESOURCE_PATH="$MODELS_PATH:$WORKSPACE_DIR/src:$IGN_GAZEBO_RESOURCE_PATH"
export GAZEBO_MODEL_PATH="$MODELS_PATH:$WORKSPACE_DIR/src:$GAZEBO_MODEL_PATH"

# Display config
export DISPLAY="${DISPLAY:-:1}"
export XAUTHORITY="${XAUTHORITY:-/run/user/1000/gdm/Xauthority}"

echo "=================================================================="
echo "🎖️  LAUNCHING ARMY BORDER MINEFIELD ENVIRONMENT"
echo "=================================================================="
echo "📍 World:     $WORLD_PATH"
echo "📦 Models:    $MODELS_PATH"
echo "🖥️  Display:   $DISPLAY"
echo "🔒 Partition: $GZ_PARTITION"
echo "=================================================================="

# Source ROS 2 if available
if [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
fi

if [ -f "$WORKSPACE_DIR/install/setup.bash" ]; then
    source "$WORKSPACE_DIR/install/setup.bash"
fi

MODE="${1:-gui}"

if [ "$MODE" == "headless" ]; then
    echo "Starting Gazebo in HEADLESS mode..."
    gz sim -s -r --headless-rendering "$WORLD_PATH"
elif [ "$MODE" == "ros2" ]; then
    echo "Starting via ROS 2 launch system..."
    ros2 launch army_border_world army_mine_world.launch.py gui:=true
elif [ "$MODE" == "amr" ]; then
    echo "Launching Gazebo Army World and spawning All-Terrain AMR..."
    # Launch Gazebo in background then spawn AMR
    gz sim -r "$WORLD_PATH" &
    sleep 3
    ros2 launch army_mine_amr spawn_amr.launch.py
elif [ "$MODE" == "slam" ]; then
    echo "Launching Complete Army Border Simulation with AMR, 4D LiDAR, SLAM, and Defusal..."
    ros2 launch army_mine_amr army_border_with_amr.launch.py
elif [ "$MODE" == "teleop" ]; then
    echo "Starting AMR Keyboard Teleop & Defusal Console..."
    ros2 run army_mine_amr amr_teleop_keyboard.py
elif [ "$MODE" == "remote" ]; then
    echo "Starting NIPUN AMR Army Executive Virtual Remote Controller..."
    python3 "$WORKSPACE_DIR/src/army_mine_amr/scripts/virtual_remote_controller.py"
elif [ "$MODE" == "rviz" ]; then
    echo "Starting Mine Tracker Node and RViz2 visualization..."
    ros2 launch army_border_world view_mines_rviz.launch.py
else
    echo "Launching Gazebo Sim GUI with army border world..."
    gz sim -r "$WORLD_PATH"
fi

