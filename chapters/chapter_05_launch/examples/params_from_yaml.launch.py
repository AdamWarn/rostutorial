import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    """
    Launch file that loads parameters from a YAML file.
    
    YAML files make it easy to manage many parameters and
    keep your launch files clean.
    """
    
    # Get the package directory
    # This works on any computer, regardless of where ROS2 is installed
    pkg_share = get_package_share_directory('my_robot_bringup')
    
    # Build path to config file
    # os.path.join combines paths correctly for any operating system
    config_file = os.path.join(
        pkg_share,
        'config',
        'robot_params.yaml'
    )
    
    return LaunchDescription([
        Node(
            package='my_robot_pkg',
            executable='parameterized_talker',
            name='talker',
            parameters=[config_file],  # Load all parameters from file
            output='screen'
        ),
    ])
