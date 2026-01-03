#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from tf2_ros import TransformListener, Buffer, TransformException
from geometry_msgs.msg import PointStamped
from rclpy.duration import Duration
import tf2_geometry_msgs


class PointTransformer(Node):
    """Transforms points from one coordinate frame to another."""
    
    def __init__(self):
        super().__init__('point_transformer')
        
        # Create TF buffer and listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # Timer to demonstrate point transformation
        self.timer = self.create_timer(2.0, self.transform_point)
        
        self.get_logger().info('Point transformer started')
    
    def transform_point(self):
        """Transform a point from lidar_link to base_link."""
        # Create point in LiDAR frame (e.g., obstacle detected at 2m forward)
        point_in_lidar = PointStamped()
        point_in_lidar.header.frame_id = 'lidar_link'
        point_in_lidar.header.stamp = self.get_clock().now().to_msg()
        
        # Obstacle 2m forward, 1m to the left
        point_in_lidar.point.x = 2.0
        point_in_lidar.point.y = 1.0
        point_in_lidar.point.z = 0.0
        
        try:
            # Transform to base_link frame
            point_in_base = self.tf_buffer.transform(
                point_in_lidar,
                'base_link',
                timeout=Duration(seconds=1.0))
            
            self.get_logger().info(
                f'Point in lidar_link: '
                f'({point_in_lidar.point.x:.2f}, '
                f'{point_in_lidar.point.y:.2f}, '
                f'{point_in_lidar.point.z:.2f})\n'
                f'  → base_link: '
                f'({point_in_base.point.x:.2f}, '
                f'{point_in_base.point.y:.2f}, '
                f'{point_in_base.point.z:.2f})')
            
        except TransformException as ex:
            self.get_logger().error(f'Transform failed: {ex}')


def main(args=None):
    rclpy.init(args=args)
    node = PointTransformer()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
