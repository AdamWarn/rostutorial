from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """
    Simple launch file that starts two nodes.
    
    This is the most basic launch file - it just starts nodes
    with default settings.
    """
    
    return LaunchDescription([
        # First node - Publisher
        Node(
            package='my_robot_pkg',     # Package containing the node
            executable='simple_publisher',  # Node executable name
            name='my_publisher',        # Custom name for this instance
            output='screen'             # Show output in terminal
        ),
        
        # Second node - Subscriber  
        Node(
            package='my_robot_pkg',
            executable='simple_subscriber',
            name='my_subscriber',
            output='screen'
        ),
    ])
