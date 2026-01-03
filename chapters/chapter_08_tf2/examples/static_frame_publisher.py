#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import StaticTransformBroadcaster


class StaticFramePublisher(Node):
    """Publishes a static transform for a sensor mounted on the robot."""
    
    def __init__(self):
        super().__init__('static_frame_publisher')
        
        # Declare parameters
        self.declare_parameter('parent_frame', 'base_link')
        self.declare_parameter('child_frame', 'lidar_link')
        self.declare_parameter('x', 0.2)
        self.declare_parameter('y', 0.0)
        self.declare_parameter('z', 0.15)
        self.declare_parameter('roll', 0.0)
        self.declare_parameter('pitch', 0.0)
        self.declare_parameter('yaw', 0.0)
        
        # Get parameters
        parent = self.get_parameter('parent_frame').value
        child = self.get_parameter('child_frame').value
        x = self.get_parameter('x').value
        y = self.get_parameter('y').value
        z = self.get_parameter('z').value
        roll = self.get_parameter('roll').value
        pitch = self.get_parameter('pitch').value
        yaw = self.get_parameter('yaw').value
        
        # Create static transform broadcaster
        self.broadcaster = StaticTransformBroadcaster(self)
        
        # Create transform message
        static_transform = TransformStamped()
        static_transform.header.stamp = self.get_clock().now().to_msg()
        static_transform.header.frame_id = parent
        static_transform.child_frame_id = child
        
        # Set translation
        static_transform.transform.translation.x = float(x)
        static_transform.transform.translation.y = float(y)
        static_transform.transform.translation.z = float(z)
        
        # Convert Euler to quaternion
        from tf_transformations import quaternion_from_euler
        q = quaternion_from_euler(roll, pitch, yaw)
        
        static_transform.transform.rotation.x = q[0]
        static_transform.transform.rotation.y = q[1]
        static_transform.transform.rotation.z = q[2]
        static_transform.transform.rotation.w = q[3]
        
        # Broadcast transform
        self.broadcaster.sendTransform(static_transform)
        
        self.get_logger().info(
            f'Published static transform: {parent} → {child} '
            f'at ({x:.2f}, {y:.2f}, {z:.2f})')


def main(args=None):
    rclpy.init(args=args)
    node = StaticFramePublisher()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
