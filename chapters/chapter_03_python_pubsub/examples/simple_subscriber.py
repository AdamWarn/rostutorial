#!/usr/bin/env python3
"""
Simple Subscriber Node
Listens to /chatter topic and prints received messages
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimpleSubscriber(Node):
    """
    A simple subscriber node that receives messages.
    
    This demonstrates:
    - Creating a ROS2 node class
    - Creating a subscriber
    - Handling incoming messages with a callback
    """
    
    def __init__(self):
        # Initialize the node with a name
        super().__init__('simple_subscriber')
        
        # Create a subscriber
        # - Message type: String
        # - Topic name: '/chatter'
        # - Callback function: listener_callback
        # - Queue size: 10
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10
        )
        self.subscription  # prevent unused variable warning
        
        # Log that we've started
        self.get_logger().info('Simple Subscriber has started!')
    
    def listener_callback(self, msg):
        """
        This function is called every time a message arrives on /chatter.
        
        Args:
            msg (String): The received message
        """
        # Log what we received
        self.get_logger().info(f'I heard: "{msg.data}"')


def main(args=None):
    """Main function to start the node"""
    # Initialize the ROS2 Python library
    rclpy.init(args=args)
    
    # Create our subscriber node
    node = SimpleSubscriber()
    
    # Keep the node running (and calling callbacks)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    
    # Cleanup
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
