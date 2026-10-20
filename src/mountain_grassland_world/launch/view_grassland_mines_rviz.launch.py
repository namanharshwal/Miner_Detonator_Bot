import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_grassland_dir = '/home/nammy/army_mine_bot/src/mountain_grassland_world'
    rviz_config = os.path.join(pkg_grassland_dir, 'rviz', 'mountain_grassland_slam.rviz')

    tracker_node = Node(
        package='mountain_grassland_world',
        executable='grassland_mine_tracker_node.py',
        name='grassland_mine_tracker_node',
        output='screen'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config]
    )

    return LaunchDescription([
        tracker_node,
        rviz_node
    ])
