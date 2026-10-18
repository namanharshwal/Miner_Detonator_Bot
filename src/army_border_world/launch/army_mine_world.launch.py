import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.conditions import IfCondition, UnlessCondition

def generate_launch_description():
    pkg_share = get_package_share_directory('army_border_world')
    world_file = os.path.join(pkg_share, 'worlds', 'army_border_minefield.sdf')
    models_path = os.path.join(pkg_share, 'models')

    # Environment variables for Gazebo model resource lookup
    env_gz_sim = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[models_path, ':', os.environ.get('GZ_SIM_RESOURCE_PATH', '')]
    )
    env_ign_sim = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=[models_path, ':', os.environ.get('IGN_GAZEBO_RESOURCE_PATH', '')]
    )
    env_classic = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=[models_path, ':', os.environ.get('GAZEBO_MODEL_PATH', '')]
    )

    # Launch arguments
    use_gui_arg = DeclareLaunchArgument(
        'gui',
        default_value='true',
        description='Launch Gazebo with GUI window (true/false)'
    )
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=world_file,
        description='Path to the SDF world file'
    )

    # Command to run Gazebo Sim
    # Using gz sim or ign gazebo
    # If gui is true: gz sim -r <world>
    # If gui is false: gz sim -s -r --headless-rendering <world>
    
    gz_gui = ExecuteProcess(
        condition=IfCondition(LaunchConfiguration('gui')),
        cmd=['gz', 'sim', '-r', LaunchConfiguration('world')],
        output='screen'
    )

    gz_headless = ExecuteProcess(
        condition=UnlessCondition(LaunchConfiguration('gui')),
        cmd=['gz', 'sim', '-s', '-r', '--headless-rendering', LaunchConfiguration('world')],
        output='screen'
    )

    return LaunchDescription([
        env_gz_sim,
        env_ign_sim,
        env_classic,
        use_gui_arg,
        world_arg,
        gz_gui,
        gz_headless
    ])
