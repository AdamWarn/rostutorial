#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from tf2_ros import TransformListener, Buffer, TransformException
from rclpy.duration import Duration


class FrameListener(Node):
    """Listens to transforms and prints frame relationships."""
    
    def __init__(self):
        super().__init__('frame_listener')
        
        # Declare parameters
        self.declare_parameter('target_frame', 'base_link')
        self.declare_parameter('source_frame', 'lidar_link')
        
        target = self.get_parameter('target_frame').value
        source = self.get_parameter('source_frame').value
        
        # Create TF buffer and listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # Store frames
        self.target_frame = target
        self.source_frame = source
        
        # Timer to lookup transforms
        self.timer = self.create_timer(1.0, self.on_timer)
        
        self.get_logger().info(
            f'Listening for transform: {target} -> {source}')
    
    def on_timer(self):
        """Periodically lookup and print transform."""
        try:
            # Get current time
            now = rclpy.time.Time()
            
            # Lookup transform
            trans = self.tf_buffer.lookup_transform(
                self.target_frame,
                self.source_frame,
                now,
                timeout=Duration(seconds=1.0))
            
            # Extract translation
            tx = trans.transform.translation.x
            ty = trans.transform.translation.y
            tz = trans.transform.translation.z
            
            # Extract rotation (quaternion)
            rx = trans.transform.rotation.x
            ry = trans.transform.rotation.y
            rz = trans.transform.rotation.z
            rw = trans.transform.rotation.w
            
            # Convert to Euler for easier reading
            from tf_transformations import euler_from_quaternion
            roll, pitch, yaw = euler_from_quaternion([rx, ry, rz, rw])
            
            self.get_logger().info(
                f'Transform {self.target_frame} → {self.source_frame}:\n'
                f'  Translation: x={tx:.3f}, y={ty:.3f}, z={tz:.3f}\n'
                f'  Rotation: roll={roll:.3f}, pitch={pitch:.3f}, yaw={yaw:.3f}')
            
        except TransformException as ex:
            self.get_logger().warn(
                f'Could not transform {self.target_frame} to {self.source_frame}: {ex}')


def main(args=None):
    rclpy.init(args=args)
    node = FrameListener()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
