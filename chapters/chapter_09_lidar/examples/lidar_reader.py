#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class LidarReader(Node):
    """Basic LiDAR data reader."""
    
    def __init__(self):
        super().__init__('lidar_reader')
        
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)
        
        self.get_logger().info('LiDAR reader started - listening to /scan')
    
    def scan_callback(self, msg):
        """Process each LiDAR scan."""
        # Get basic info
        num_readings = len(msg.ranges)
        
        # Filter valid readings
        valid_ranges = [r for r in msg.ranges 
                       if msg.range_min < r < msg.range_max]
        
        if not valid_ranges:
            self.get_logger().warn('No valid readings in this scan')
            return
        
        # Calculate statistics
        min_distance = min(valid_ranges)
        max_distance = max(valid_ranges)
        avg_distance = sum(valid_ranges) / len(valid_ranges)
        
        # Find angle of closest obstacle
        min_index = msg.ranges.index(min_distance)
        min_angle = msg.angle_min + min_index * msg.angle_increment
        
        self.get_logger().info(
            f'Scan: {num_readings} readings | '
            f'Valid: {len(valid_ranges)} | '
            f'Min: {min_distance:.2f}m @ {min_angle:.2f}rad | '
            f'Max: {max_distance:.2f}m | '
            f'Avg: {avg_distance:.2f}m')


def main(args=None):
    rclpy.init(args=args)
    node = LidarReader()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
