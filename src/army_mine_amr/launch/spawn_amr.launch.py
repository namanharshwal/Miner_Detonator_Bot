import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = '/home/nammy/army_mine_bot/src/army_mine_amr'
    urdf_path = os.path.join(pkg_dir, 'urdf', 'army_mine_amr.urdf')
    bridge_config = os.path.join(pkg_dir, 'config', 'ros_gz_bridge.yaml')

    with open(urdf_path, 'r') as f:
        robot_desc = f.read()

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True
        }]
    )

    # ROS-GZ Bridge
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        parameters=[{
            'config_file': bridge_config,
            'use_sim_time': True
        }]
    )

    return LaunchDescription([
        robot_state_publisher,
        gz_bridge
    ])
