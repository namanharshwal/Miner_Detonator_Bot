import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_grassland_dir = '/home/nammy/army_mine_bot/src/mountain_grassland_world'
    pkg_amr_dir = '/home/nammy/army_mine_bot/src/army_mine_amr'
    pkg_border_dir = '/home/nammy/army_mine_bot/src/army_border_world'

    world_sdf = os.path.join(pkg_grassland_dir, 'worlds', 'mountain_grassland_minefield.sdf')
    models_path = f"{pkg_grassland_dir}/models:{pkg_border_dir}/models:{pkg_amr_dir}/..:{os.path.join(pkg_amr_dir, 'models')}"
    urdf_path = os.path.join(pkg_amr_dir, 'urdf', 'army_mine_amr.urdf')
    slam_config = os.path.join(pkg_amr_dir, 'config', 'slam_toolbox_params.yaml')
    rviz_config = os.path.join(pkg_grassland_dir, 'rviz', 'mountain_grassland_slam.rviz')

    with open(urdf_path, 'r') as f:
        robot_desc = f.read()

    # Environment variables
    gz_env = {
        'GZ_PARTITION': 'army_mine_bot',
        'IGN_PARTITION': 'army_mine_bot',
        'GZ_IP': '127.0.0.1',
        'IGN_IP': '127.0.0.1',
        'ROS_DOMAIN_ID': '42',
        'GZ_SIM_RESOURCE_PATH': f"{models_path}:{os.environ.get('GZ_SIM_RESOURCE_PATH', '')}",
        'IGN_GAZEBO_RESOURCE_PATH': f"{models_path}:{os.environ.get('IGN_GAZEBO_RESOURCE_PATH', '')}",
        'GAZEBO_MODEL_PATH': f"{models_path}:{os.environ.get('GAZEBO_MODEL_PATH', '')}",
        'DISPLAY': os.environ.get('DISPLAY', ':1'),
        'XAUTHORITY': os.environ.get('XAUTHORITY', '/run/user/1000/gdm/Xauthority')
    }
    for k, v in gz_env.items():
        os.environ[k] = v

    # 1. Gazebo Sim Process (Alpine Mountain Grassland World)
    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_sdf],
        output='screen',
        additional_env=gz_env
    )

    # 2. Robot State Publisher
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

    # 3. Native Gazebo Harmonic <-> ROS 2 Bridge (4D LiDAR, Depth Camera, Odom, IMU, CmdVel)
    gz_bridge = Node(
        package='army_mine_amr',
        executable='gz_harmonic_bridge.py',
        name='gz_harmonic_bridge',
        output='screen',
        additional_env=gz_env
    )

    # 4. Grassland Mine Tracker Node (18 NIPUN AP Minelets & W-Formation Stations)
    grassland_tracker = Node(
        package='mountain_grassland_world',
        executable='grassland_mine_tracker_node.py',
        name='grassland_mine_tracker_node',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    # 5. NIPUN Mine-Laying & W-Formation Controller (Downloads/1.docx requirements)
    mine_laying_controller = Node(
        package='army_mine_amr',
        executable='amr_mine_laying_controller.py',
        name='amr_mine_laying_controller',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    # 6. SLAM Toolbox Node (Async 2D Occupancy Grid Mapping)
    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_config, {'use_sim_time': True}]
    )

    # 7. RViz2 Visualization (Side-by-side with Gazebo)
    rviz_args = ['-geometry', '1380x1520+1460+35']
    if os.path.exists(rviz_config):
        rviz_args.extend(['-d', rviz_config])

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=rviz_args,
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        gz_sim,
        robot_state_publisher,
        gz_bridge,
        grassland_tracker,
        mine_laying_controller,
        slam_node,
        rviz_node
    ])
