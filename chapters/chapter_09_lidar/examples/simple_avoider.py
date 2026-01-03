#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import math


class SimpleAvoider(Node):
    """Simple obstacle avoidance using LiDAR."""
    
    def __init__(self):
        super().__init__('simple_avoider')
        
        # Declare parameters
        self.declare_parameter('safe_distance', 1.0)
        self.declare_parameter('linear_speed', 0.2)
        self.declare_parameter('angular_speed', 0.5)
        
        # Get parameters
        self.safe_distance = self.get_parameter('safe_distance').value
        self.linear_speed = self.get_parameter('linear_speed').value
        self.angular_speed = self.get_parameter('angular_speed').value
        
        # Subscribe to LiDAR
        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
        
        # Publish velocity commands
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.get_logger().info(
            f'Obstacle avoider started | '
            f'Safe distance: {self.safe_distance}m')
    
    def is_sector_clear(self, msg, start_angle, end_angle):
        """Check if angular sector has obstacles."""
        # Calculate index range
        start_idx = int((start_angle - msg.angle_min) / msg.angle_increment)
        end_idx = int((end_angle - msg.angle_min) / msg.angle_increment)
        
        # Clamp to valid range
        start_idx = max(0, start_idx)
        end_idx = min(len(msg.ranges), end_idx)
        
        # Check all ranges in sector
        for i in range(start_idx, end_idx):
            r = msg.ranges[i]
            
            # Valid reading below safe threshold?
            if msg.range_min < r < msg.range_max:
                if r < self.safe_distance:
                    return False
        
        return True
    
    def scan_callback(self, msg):
        """React to LiDAR data."""
        cmd = Twist()
        
        # Check front sector (±45°)
        front_clear = self.is_sector_clear(
            msg,
            -math.pi / 4,
            math.pi / 4)
        
        # Check left sector
        left_clear = self.is_sector_clear(
            msg,
            math.pi / 4,
            3 * math.pi / 4)
        
        # Check right sector
        right_clear = self.is_sector_clear(
            msg,
            -3 * math.pi / 4,
            -math.pi / 4)
        
        # Decision logic
        if front_clear:
            # Path clear - move forward
            cmd.linear.x = self.linear_speed
            cmd.angular.z = 0.0
            self.get_logger().info('Moving forward', throttle_duration_sec=2.0)
        
        elif left_clear:
            # Turn left
            cmd.linear.x = 0.0
            cmd.angular.z = self.angular_speed
            self.get_logger().warn('Turning left', throttle_duration_sec=2.0)
        
        elif right_clear:
            # Turn right
            cmd.linear.x = 0.0
            cmd.angular.z = -self.angular_speed
            self.get_logger().warn('Turning right', throttle_duration_sec=2.0)
        
        else:
            # Surrounded! Stop and rotate
            cmd.linear.x = 0.0
            cmd.angular.z = self.angular_speed
            self.get_logger().error('Stuck! Rotating...', throttle_duration_sec=2.0)
        
        # Publish command
        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = SimpleAvoider()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Stop robot on exit
        cmd = Twist()
        node.cmd_pub.publish(cmd)
        
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
