import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    pkg_world_dir = '/home/nammy/army_mine_bot/src/mountain_grassland_world'
    pkg_amr_dir = '/home/nammy/army_mine_bot/src/army_mine_amr'
    models_path = f"{pkg_world_dir}/models:{pkg_amr_dir}/..:{os.path.join(pkg_amr_dir, 'models')}"
    world_sdf = os.path.join(pkg_world_dir, 'worlds', 'mountain_grassland_minefield.sdf')

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

    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_sdf],
        output='screen',
        additional_env=gz_env
    )

    return LaunchDescription([
        gz_sim
    ])
