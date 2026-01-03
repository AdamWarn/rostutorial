#!/usr/bin/env python3
"""
Simple Publisher Node
Publishes "Hello World" messages to /chatter topic
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimplePublisher(Node):
    """
    A simple publisher node that sends messages periodically.
    
    This demonstrates:
    - Creating a ROS2 node class
    - Creating a publisher
    - Using a timer for periodic execution
    """
    
    def __init__(self):
        # Initialize the node with a name
        super().__init__('simple_publisher')
        
        # Create a publisher
        # - Message type: String
        # - Topic name: '/chatter'
        # - Queue size: 10 (how many messages to buffer)
        self.publisher_ = self.create_publisher(String, 'chatter', 10)
        
        # Create a timer that calls our callback every 0.5 seconds
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        # Counter for our messages
        self.counter = 0
        
        # Log that we've started
        self.get_logger().info('Simple Publisher has started!')
    
    def timer_callback(self):
        """
        This function is called every 0.5 seconds by the timer.
        It creates and publishes a message.
        """
        # Create a message
        msg = String()
        msg.data = f'Hello World: {self.counter}'
        
        # Publish the message
        self.publisher_.publish(msg)
        
        # Log what we published
        self.get_logger().info(f'Publishing: "{msg.data}"')
        
        # Increment counter
        self.counter += 1


def main(args=None):
    """Main function to start the node"""
    # Initialize the ROS2 Python library
    rclpy.init(args=args)
    
    # Create our publisher node
    node = SimplePublisher()
    
    # Keep the node running (and calling callbacks)
    # This blocks until you press Ctrl+C
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    
    # Cleanup
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
