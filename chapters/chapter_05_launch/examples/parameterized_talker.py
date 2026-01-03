#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ParameterizedTalker(Node):
    """
    A publisher node that uses parameters for configuration.
    
    This demonstrates how to make nodes flexible and configurable
    without changing code.
    """
    
    def __init__(self):
        super().__init__('parameterized_talker')
        
        # Declare parameters with default values
        # Format: declare_parameter(name, default_value)
        self.declare_parameter('message_text', 'Hello ROS2!')
        self.declare_parameter('publish_rate', 1.0)  # Hz
        self.declare_parameter('topic_name', 'chatter')
        
        # Get parameter values
        message = self.get_parameter('message_text').value
        rate = self.get_parameter('publish_rate').value
        topic = self.get_parameter('topic_name').value
        
        # Store for later use
        self.message_text = message
        
        # Create publisher
        self.publisher = self.create_publisher(String, topic, 10)
        
        # Create timer based on rate parameter
        # 1.0 / rate converts Hz to seconds
        # Example: rate=2Hz means timer every 0.5 seconds
        timer_period = 1.0 / rate
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        # Counter for unique messages
        self.counter = 0
        
        # Log configuration
        self.get_logger().info(f'Started with message: "{message}"')
        self.get_logger().info(f'Publishing to /{topic} at {rate} Hz')
    
    def timer_callback(self):
        """Called repeatedly by the timer."""
        # Create message
        msg = String()
        msg.data = f'{self.message_text} (count: {self.counter})'
        
        # Publish
        self.publisher.publish(msg)
        
        # Log (throttled to avoid spam)
        self.get_logger().info(
            f'Published: "{msg.data}"',
            throttle_duration_sec=5.0  # Only log every 5 seconds
        )
        
        # Increment counter
        self.counter += 1


def main(args=None):
    # Initialize ROS2
    rclpy.init(args=args)
    
    # Create node
    node = ParameterizedTalker()
    
    try:
        # Keep node running
        rclpy.spin(node)
    except KeyboardInterrupt:
        # User pressed Ctrl+C
        pass
    finally:
        # Cleanup
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
