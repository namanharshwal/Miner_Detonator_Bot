#!/bin/bash
# ==============================================================================
# Master Launcher for NIPUN AMR Army Executive Virtual Remote Controller
# ==============================================================================
set -e

WORKSPACE_DIR="/home/nammy/army_mine_bot"

# Environment & Display Setup
export DISPLAY="${DISPLAY:-:1}"
export XAUTHORITY="${XAUTHORITY:-/run/user/1000/gdm/Xauthority}"
export GZ_PARTITION=army_mine_bot
export ROS_DOMAIN_ID=42

# Source ROS 2 Humble
if [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
fi

# Source Workspace
if [ -f "$WORKSPACE_DIR/install/setup.bash" ]; then
    source "$WORKSPACE_DIR/install/setup.bash"
fi

echo "=================================================================="
echo "🎖️  LAUNCHING NIPUN AMR ARMY EXECUTIVE VIRTUAL REMOTE CONTROLLER"
echo "=================================================================="
echo "🖥️  Target Display: $DISPLAY"
echo "🔒 ROS Domain:     $ROS_DOMAIN_ID"
echo "📡 GZ Partition:   $GZ_PARTITION"
echo "=================================================================="

exec python3 "$WORKSPACE_DIR/src/army_mine_amr/scripts/virtual_remote_controller.py" "$@"
