from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """
    Launch file with command-line arguments.
    
    Users can customize behavior when launching:
    ros2 launch my_pkg this_file.launch.py use_sim_time:=true
    """
    
    # Declare arguments (like function parameters)
    # These can be overridden from command line
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) time when true'
    )
    
    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='my_robot',
        description='Name of the robot'
    )
    
    publish_rate_arg = DeclareLaunchArgument(
        'publish_rate',
        default_value='1.0',
        description='Publishing frequency in Hz'
    )
    
    # Get argument values (to use in nodes)
    # LaunchConfiguration reads the argument value
    use_sim_time = LaunchConfiguration('use_sim_time')
    robot_name = LaunchConfiguration('robot_name')
    publish_rate = LaunchConfiguration('publish_rate')
    
    # Create node with arguments
    talker_node = Node(
        package='my_robot_pkg',
        executable='parameterized_talker',
        name='talker',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_name': robot_name,
            'publish_rate': publish_rate,
            'message_text': 'Hello from configured robot!'
        }],
        output='screen'
    )
    
    # Return everything
    return LaunchDescription([
        # Arguments must be in the list
        use_sim_time_arg,
        robot_name_arg,
        publish_rate_arg,
        # Then nodes
        talker_node,
    ])
