#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import math


class DirectionalLidar(Node):
    """Query LiDAR distances in specific directions."""
    
    def __init__(self):
        super().__init__('directional_lidar')
        
        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
        
        self.get_logger().info('Directional LiDAR analyzer started')
    
    def get_distance_at_angle(self, msg, target_angle):
        """
        Get distance measurement at specific angle.
        
        Args:
            msg: LaserScan message
            target_angle: Desired angle in radians (0 = straight ahead)
        
        Returns:
            float: Distance in meters (or inf if invalid)
        """
        # Calculate index for target angle
        if msg.angle_increment == 0:
            return float('inf')
        
        index = int((target_angle - msg.angle_min) / msg.angle_increment)
        
        # Clamp to valid range
        index = max(0, min(index, len(msg.ranges) - 1))
        
        return msg.ranges[index]
    
    def scan_callback(self, msg):
        """Check distances in cardinal directions."""
        # Define directions (radians)
        directions = {
            'Front': 0.0,
            'Front-Left': math.pi / 4,
            'Left': math.pi / 2,
            'Back-Left': 3 * math.pi / 4,
            'Back': math.pi,
            'Back-Right': -3 * math.pi / 4,
            'Right': -math.pi / 2,
            'Front-Right': -math.pi / 4,
        }
        
        # Query each direction
        results = []
        for name, angle in directions.items():
            distance = self.get_distance_at_angle(msg, angle)
            
            # Format output
            if math.isinf(distance):
                results.append(f'{name}: ∞')
            else:
                results.append(f'{name}: {distance:.2f}m')
        
        # Log results
        self.get_logger().info(' | '.join(results))


def main(args=None):
    rclpy.init(args=args)
    node = DirectionalLidar()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
