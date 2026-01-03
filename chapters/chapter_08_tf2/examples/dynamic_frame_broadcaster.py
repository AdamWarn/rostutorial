#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import math


class DynamicFrameBroadcaster(Node):
    """Simulates a moving robot by broadcasting dynamic transforms."""
    
    def __init__(self):
        super().__init__('dynamic_frame_broadcaster')
        
        # Create transform broadcaster
        self.broadcaster = TransformBroadcaster(self)
        
        # Robot state (simulated)
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.linear_velocity = 0.5  # m/s
        self.angular_velocity = 0.3  # rad/s
        
        # Publish transforms at 50Hz
        self.timer = self.create_timer(0.02, self.publish_transform)
        self.get_logger().info('Dynamic frame broadcaster started')
    
    def publish_transform(self):
        """Publish odom -> base_link transform."""
        # Update simulated robot position
        dt = 0.02  # 50Hz
        self.x += self.linear_velocity * math.cos(self.yaw) * dt
        self.y += self.linear_velocity * math.sin(self.yaw) * dt
        self.yaw += self.angular_velocity * dt
        
        # Create transform message
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        
        # Set translation
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        
        # Set rotation (quaternion from yaw)
        from tf_transformations import quaternion_from_euler
        q = quaternion_from_euler(0, 0, self.yaw)
        
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]
        
        # Broadcast transform
        self.broadcaster.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = DynamicFrameBroadcaster()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
