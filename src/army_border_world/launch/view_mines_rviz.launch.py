import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('army_border_world')
    rviz_config = os.path.join(pkg_share, 'rviz', 'army_mine_world.rviz')

    tracker_node = Node(
        package='army_border_world',
        executable='mine_tracker_node.py',
        name='mine_tracker_node',
        output='screen'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        output='screen'
    )

    return LaunchDescription([
        tracker_node,
        rviz_node
    ])
