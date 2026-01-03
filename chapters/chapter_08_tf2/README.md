# Chapter 8: TF2 - Coordinate Frames & Transformations

**Goal**: Understand how ROS2 tracks the position and orientation of all robot parts in 3D space.

---

## 📖 What is TF2?

**TF2 (Transform Library 2)** is ROS2's system for tracking coordinate frames over time.

**Why do we need it?**
- LiDAR detects obstacle at (2, 1) relative to its frame
- But where is that in the world?
- Where is it relative to the wheels?
- TF2 answers these questions!

---

## 🎯 Coordinate Frames Explained

Every part of your robot has its own coordinate frame:

```
world
  └─ odom
      └─ base_link (robot center)
          ├─ left_wheel
          ├─ right_wheel
          ├─ lidar_link
          └─ camera_link
```

**Key Frames**:
- `world`: Fixed global origin
- `odom`: Odometry frame (continuous, can drift)
- `map`: Map frame (corrected by SLAM)
- `base_link`: Robot's center
- `lidar_link`, `camera_link`: Sensor frames

---

## 🔄 Transform Tree

Transforms describe how frames relate:

```
base_link is 0.2m forward, 0.15m up from lidar_link
      ↓
Transform: (x=0.2, y=0, z=0.15)
```

TF2 automatically chains transforms:
```
lidar → base_link → odom → map
```

So you can ask: "Where is the LiDAR point in the map frame?"

---

## 👁️ Viewing the TF Tree

```bash
# Install tools
sudo apt install ros-jazzy-tf2-tools ros-jazzy-tf2-ros

# View TF tree (after launching robot)
ros2 run tf2_tools view_frames

# Creates frames.pdf - open it!
evince frames.pdf

# Or view in terminal
ros2 run tf2_ros tf2_echo base_link lidar_link
```

---

## 💻 Broadcasting Transforms

### Static Transforms (Never Change)

For fixed parts like sensors:

```bash
# Command line (temporary)
ros2 run tf2_ros static_transform_publisher \
  0.2 0 0.15 0 0 0 base_link lidar_link
```

**In Python**:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import StaticTransformBroadcaster

class StaticFramePublisher(Node):
    def __init__(self):
        super().__init__('static_frame_publisher')
        
        self.broadcaster = StaticTransformBroadcaster(self)
        
        # Create transform
        static_transform = TransformStamped()
        static_transform.header.stamp = self.get_clock().now().to_msg()
        static_transform.header.frame_id = 'base_link'
        static_transform.child_frame_id = 'lidar_link'
        
        # Translation
        static_transform.transform.translation.x = 0.2
        static_transform.transform.translation.y = 0.0
        static_transform.transform.translation.z = 0.15
        
        # Rotation (quaternion) - no rotation
        static_transform.transform.rotation.x = 0.0
        static_transform.transform.rotation.y = 0.0
        static_transform.transform.rotation.z = 0.0
        static_transform.transform.rotation.w = 1.0
        
        self.broadcaster.sendTransform(static_transform)
        self.get_logger().info('Static transform published!')
```

### Dynamic Transforms (Change Over Time)

For moving parts like robot position:

```python
from tf2_ros import TransformBroadcaster

class DynamicFramePublisher(Node):
    def __init__(self):
        super().__init__('dynamic_frame_publisher')
        
        self.broadcaster = TransformBroadcaster(self)
        self.timer = self.create_timer(0.1, self.publish_transform)
        
    def publish_transform(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        
        # Update based on robot movement
        t.transform.translation.x = self.robot_x
        t.transform.translation.y = self.robot_y
        t.transform.translation.z = 0.0
        
        # Rotation (from yaw angle)
        from tf_transformations import quaternion_from_euler
        q = quaternion_from_euler(0, 0, self.robot_yaw)
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]
        
        self.broadcaster.sendTransform(t)
```

---

## 🔍 Listening to Transforms

**Look up transforms between frames**:

```python
from tf2_ros import TransformListener, Buffer
from rclpy.duration import Duration

class FrameListener(Node):
    def __init__(self):
        super().__init__('frame_listener')
        
        # Create buffer and listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # Call timer
        self.timer = self.create_timer(1.0, self.on_timer)
    
    def on_timer(self):
        try:
            # Look up transform from base_link to lidar_link
            now = rclpy.time.Time()
            trans = self.tf_buffer.lookup_transform(
                'base_link',
                'lidar_link',
                now,
                timeout=Duration(seconds=1.0))
            
            self.get_logger().info(
                f'LiDAR is at: '
                f'x={trans.transform.translation.x:.2f}, '
                f'y={trans.transform.translation.y:.2f}, '
                f'z={trans.transform.translation.z:.2f}')
            
        except Exception as ex:
            self.get_logger().warn(f'Could not transform: {ex}')
```

---

## 🎯 Transforming Points

**Transform a point from one frame to another**:

```python
from tf2_ros import TransformException
from geometry_msgs.msg import PointStamped
import tf2_geometry_msgs

class PointTransformer(Node):
    def __init__(self):
        super().__init__('point_transformer')
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
    
    def transform_point(self):
        # Point in LiDAR frame
        point_in_lidar = PointStamped()
        point_in_lidar.header.frame_id = 'lidar_link'
        point_in_lidar.header.stamp = self.get_clock().now().to_msg()
        point_in_lidar.point.x = 2.0
        point_in_lidar.point.y = 1.0
        point_in_lidar.point.z = 0.0
        
        try:
            # Transform to base_link frame
            point_in_base = self.tf_buffer.transform(
                point_in_lidar, 'base_link',
                timeout=Duration(seconds=1.0))
            
            self.get_logger().info(
                f'Point in base_link: '
                f'({point_in_base.point.x:.2f}, '
                f'{point_in_base.point.y:.2f}, '
                f'{point_in_base.point.z:.2f})')
            
        except TransformException as ex:
            self.get_logger().error(f'Transform failed: {ex}')
```

---

## 🤖 Robot State Publisher

**Automatically publishes transforms from URDF**!

Your robot's URDF defines links and joints. `robot_state_publisher` reads this and publishes TF transforms.

```python
# Already in your Gazebo launch file from Chapter 7!
robot_state_publisher = Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    parameters=[{'robot_description': robot_desc}]
)
```

This publishes transforms for all fixed joints in your URDF automatically!

---

## 💻 Exercises

### Exercise 8.1: View Your Robot's TF Tree

```bash
# Launch your robot in Gazebo
ros2 launch my_robot_description gazebo.launch.py

# In another terminal
ros2 run tf2_tools view_frames
evince frames.pdf
```

**Questions**:
1. What is the root frame?
2. How many frames exist?
3. What's the parent of `lidar_link`?

### Exercise 8.2: Echo Transforms

```bash
# See transform between base_link and left_wheel
ros2 run tf2_ros tf2_echo base_link left_wheel

# Drive robot and watch transform change!
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### Exercise 8.3: Create Static Transform Publisher

Create a node that publishes a static transform for a GPS sensor 0.3m behind the robot:

```python
# GPS is at (-0.3, 0, 0.25) relative to base_link
```

---

## 📊 Common TF2 Frames

| Frame | Description | Parent |
|-------|-------------|--------|
| `world` | Global fixed frame | - |
| `map` | SLAM map frame | `world` |
| `odom` | Odometry frame | `map` |
| `base_link` | Robot center | `odom` |
| `base_footprint` | Robot ground projection | `base_link` |
| `lidar_link` | LiDAR sensor | `base_link` |
| `camera_link` | Camera | `base_link` |

---

## 🎓 Understanding Quaternions

Rotations in TF use quaternions (not Euler angles):

```python
# Convert Euler (roll, pitch, yaw) to quaternion
from tf_transformations import quaternion_from_euler

roll = 0.0
pitch = 0.0
yaw = 1.5708  # 90 degrees in radians

q = quaternion_from_euler(roll, pitch, yaw)
# q = [x, y, z, w]

# Use in transform
t.transform.rotation.x = q[0]
t.transform.rotation.y = q[1]
t.transform.rotation.z = q[2]
t.transform.rotation.w = q[3]
```

**Install tf_transformations**:
```bash
sudo apt install ros-jazzy-tf-transformations
```

---

## 🐛 Common Issues

### "Frame doesn't exist"
- Check `ros2 run tf2_tools view_frames` - is frame being published?
- Check frame name spelling (case-sensitive!)

### "Transform too old"
- Transforms have timestamps
- Use `now = rclpy.time.Time()` for latest transform
- Or use specific time if needed

### "Lookup would extrapolate into the future"
- You're asking for a future time
- Use current time or past time only

---

## 🎯 Key Takeaways

1. **TF2 tracks all coordinate frames** in your robot
2. **Static transforms** for fixed parts (sensors)
3. **Dynamic transforms** for moving parts (robot position)
4. **robot_state_publisher** publishes transforms from URDF
5. **Transform lookup** converts points between frames
6. **All ROS2 robots use TF2** - it's fundamental!

---

## 🚀 Next Chapter

[Chapter 9: LiDAR Integration](../chapter_09_lidar/README.md) - Process LiDAR data for obstacle detection and navigation!

---

## 📚 Resources

- [TF2 Tutorials](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Tf2/Tf2-Main.html)
- [tf2_ros API](https://docs.ros.org/en/jazzy/p/tf2_ros/)
- [Quaternions Explained](https://www.youtube.com/watch?v=zjMuIxRvygQ)
