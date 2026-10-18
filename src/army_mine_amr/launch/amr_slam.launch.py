import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = '/home/nammy/army_mine_bot/src/army_mine_amr'
    slam_config = os.path.join(pkg_dir, 'config', 'slam_toolbox_params.yaml')
    rviz_config = os.path.join(pkg_dir, 'rviz', 'army_mine_amr_slam.rviz')

    # SLAM Toolbox Node
    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_config, {'use_sim_time': True}]
    )

    # Defusal Controller Node
    defusal_controller = Node(
        package='army_mine_amr',
        executable='amr_mine_defusal_controller.py',
        name='amr_mine_defusal_controller',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    # RViz2 Node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config] if os.path.exists(rviz_config) else [],
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        slam_node,
        defusal_controller,
        rviz_node
    ])
