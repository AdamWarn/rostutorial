#!/usr/bin/env python3
"""
Exercise 3.4 Solution: Number Publisher & Subscriber

This shows how to publish and subscribe to Int32 messages.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32


class NumberPublisher(Node):
    """Publishes incrementing integers to /number topic"""
    
    def __init__(self):
        super().__init__('number_publisher')
        self.publisher_ = self.create_publisher(Int32, 'number', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.counter = 0
        self.get_logger().info('Number Publisher started!')
    
    def timer_callback(self):
        msg = Int32()
        msg.data = self.counter
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')
        self.counter += 1


class NumberSubscriber(Node):
    """Subscribes to /number topic and prints received integers"""
    
    def __init__(self):
        super().__init__('number_subscriber')
        self.subscription = self.create_subscription(
            Int32,
            'number',
            self.listener_callback,
            10
        )
        self.get_logger().info('Number Subscriber started!')
    
    def listener_callback(self, msg):
        self.get_logger().info(f'Received: {msg.data}')


def main_publisher(args=None):
    rclpy.init(args=args)
    node = NumberPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


def main_subscriber(args=None):
    rclpy.init(args=args)
    node = NumberSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    # This is just for reference - in a real package, you'd have separate entry points
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'pub':
        main_publisher()
    else:
        main_subscriber()
