# Chapter 9: LiDAR Sensor Integration

**Goal**: Learn to work with LiDAR sensors - the eyes of your SLAM robot!

---

## 📖 What is LiDAR?

**LiDAR (Light Detection And Ranging)** shoots laser beams in a circle, measuring distances to obstacles.

```
    Front
      ↑
      |  *  ← obstacle 2m away
      | /
      |/
  [ROBOT]
```

**Common LiDAR specs**:
- Range: 0.15m - 12m
- Scan angle: 360° (full circle)
- Scan rate: 5-10 Hz
- Angular resolution: 0.25° - 1°

**ROS2 Message**: `sensor_msgs/LaserScan`

---

## 📊 LaserScan Message

```python
# sensor_msgs/msg/LaserScan
std_msgs/Header header
float32 angle_min        # Start angle (radians)
float32 angle_max        # End angle (radians)
float32 angle_increment  # Angular distance between measurements
float32 time_increment   # Time between measurements
float32 scan_time        # Time between scans
float32 range_min        # Minimum range value (m)
float32 range_max        # Maximum range value (m)
float32[] ranges         # Range data (m) - main data!
float32[] intensities    # Intensity data (device specific)
```

**Key field: `ranges`**
- Array of distance measurements
- Index 0 = `angle_min`
- Each step increases by `angle_increment`
- `inf` = no obstacle detected
- `nan` = error/invalid reading

---

## 👁️ Visualizing LiDAR in RViz

```bash
# Launch your robot in Gazebo
ros2 launch my_robot_description gazebo.launch.py

# Open RViz
rviz2

# In RViz:
# 1. Set Fixed Frame to "base_link" or "lidar_link"
# 2. Click "Add" → "By topic" → "/scan" → "LaserScan"
# 3. You should see red dots showing obstacles!
```

**Troubleshooting**:
- No data? Check: `ros2 topic echo /scan`
- Red errors? Check Fixed Frame matches your robot's frame

---

## 💻 Reading LiDAR Data

### Basic Subscriber

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class LidarReader(Node):
    def __init__(self):
        super().__init__('lidar_reader')
        
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)
        
        self.get_logger().info('LiDAR reader started')
    
    def scan_callback(self, msg):
        """Process each LiDAR scan."""
        # Get number of readings
        num_readings = len(msg.ranges)
        
        # Get angular info
        angle_min = msg.angle_min
        angle_max = msg.angle_max
        angle_increment = msg.angle_increment
        
        self.get_logger().info(
            f'Scan: {num_readings} readings from '
            f'{angle_min:.2f} to {angle_max:.2f} rad')
        
        # Example: Get distance directly ahead (index 0 or middle)
        front_index = len(msg.ranges) // 2
        front_distance = msg.ranges[front_index]
        
        self.get_logger().info(f'Distance ahead: {front_distance:.2f}m')
```

---

## 🎯 Finding Obstacles

### Detect Nearest Obstacle

```python
class ObstacleDetector(Node):
    def __init__(self):
        super().__init__('obstacle_detector')
        
        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
        
        self.min_safe_distance = 0.5  # meters
    
    def scan_callback(self, msg):
        """Find closest obstacle."""
        # Filter out invalid readings
        valid_ranges = [r for r in msg.ranges 
                       if msg.range_min < r < msg.range_max]
        
        if not valid_ranges:
            self.get_logger().warn('No valid LiDAR readings!')
            return
        
        # Find minimum distance
        min_distance = min(valid_ranges)
        min_index = msg.ranges.index(min_distance)
        
        # Calculate angle of closest obstacle
        angle = msg.angle_min + min_index * msg.angle_increment
        
        self.get_logger().info(
            f'Closest obstacle: {min_distance:.2f}m at {angle:.2f} rad')
        
        # Safety check
        if min_distance < self.min_safe_distance:
            self.get_logger().warn('⚠️  OBSTACLE TOO CLOSE!')
```

---

## 🔍 Directional Distance Queries

### Get distance in specific direction

```python
import math

class DirectionalLidar(Node):
    def __init__(self):
        super().__init__('directional_lidar')
        
        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
    
    def get_distance_at_angle(self, msg, target_angle):
        """
        Get distance at specific angle.
        
        Args:
            msg: LaserScan message
            target_angle: Angle in radians (0 = forward)
        
        Returns:
            float: Distance in meters
        """
        # Find closest index to target angle
        index = int((target_angle - msg.angle_min) / msg.angle_increment)
        
        # Clamp to valid range
        index = max(0, min(index, len(msg.ranges) - 1))
        
        return msg.ranges[index]
    
    def scan_callback(self, msg):
        """Check distances in key directions."""
        # Forward (0°)
        front = self.get_distance_at_angle(msg, 0.0)
        
        # Left (90°)
        left = self.get_distance_at_angle(msg, math.pi / 2)
        
        # Right (-90°)
        right = self.get_distance_at_angle(msg, -math.pi / 2)
        
        # Back (180°)
        back = self.get_distance_at_angle(msg, math.pi)
        
        self.get_logger().info(
            f'F: {front:.2f}m | L: {left:.2f}m | '
            f'R: {right:.2f}m | B: {back:.2f}m')
```

---

## 🚧 Sector Analysis

### Check if sector is clear

```python
class SectorAnalyzer(Node):
    def __init__(self):
        super().__init__('sector_analyzer')
        
        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
    
    def is_sector_clear(self, msg, start_angle, end_angle, min_distance):
        """
        Check if angular sector is clear.
        
        Args:
            msg: LaserScan message
            start_angle: Start angle in radians
            end_angle: End angle in radians
            min_distance: Minimum safe distance
        
        Returns:
            bool: True if sector is clear
        """
        # Get index range
        start_idx = int((start_angle - msg.angle_min) / msg.angle_increment)
        end_idx = int((end_angle - msg.angle_min) / msg.angle_increment)
        
        # Clamp indices
        start_idx = max(0, start_idx)
        end_idx = min(len(msg.ranges), end_idx)
        
        # Check all ranges in sector
        for i in range(start_idx, end_idx):
            r = msg.ranges[i]
            
            # Valid reading within danger zone?
            if msg.range_min < r < msg.range_max and r < min_distance:
                return False
        
        return True
    
    def scan_callback(self, msg):
        """Check if front sector is clear."""
        # Check 60° cone ahead (-30° to +30°)
        front_clear = self.is_sector_clear(
            msg,
            -math.pi / 6,  # -30°
            math.pi / 6,   # +30°
            1.0)           # 1m minimum
        
        if front_clear:
            self.get_logger().info('✓ Front path clear')
        else:
            self.get_logger().warn('✗ Obstacle ahead!')
```

---

## 📉 Data Filtering

### Remove noise and outliers

```python
class LidarFilter(Node):
    def __init__(self):
        super().__init__('lidar_filter')
        
        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
        
        self.publisher = self.create_publisher(
            LaserScan, '/scan/filtered', 10)
    
    def scan_callback(self, msg):
        """Filter and republish scan."""
        filtered = LaserScan()
        filtered.header = msg.header
        filtered.angle_min = msg.angle_min
        filtered.angle_max = msg.angle_max
        filtered.angle_increment = msg.angle_increment
        filtered.time_increment = msg.time_increment
        filtered.scan_time = msg.scan_time
        filtered.range_min = msg.range_min
        filtered.range_max = msg.range_max
        
        # Filter ranges
        filtered_ranges = []
        for r in msg.ranges:
            # Replace invalid with max range
            if r < msg.range_min or r > msg.range_max:
                filtered_ranges.append(msg.range_max)
            # Remove too-close readings (noise)
            elif r < 0.2:
                filtered_ranges.append(msg.range_max)
            else:
                filtered_ranges.append(r)
        
        filtered.ranges = filtered_ranges
        filtered.intensities = msg.intensities
        
        self.publisher.publish(filtered)
```

---

## 🤖 Obstacle Avoidance Logic

### Simple reactive behavior

```python
from geometry_msgs.msg import Twist

class ObstacleAvoider(Node):
    def __init__(self):
        super().__init__('obstacle_avoider')
        
        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
        
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.safe_distance = 1.0  # meters
    
    def scan_callback(self, msg):
        """React to obstacles."""
        cmd = Twist()
        
        # Check front sector (±30°)
        front_ranges = msg.ranges[
            len(msg.ranges)//2 - 50:len(msg.ranges)//2 + 50]
        
        # Filter valid readings
        valid_front = [r for r in front_ranges 
                      if msg.range_min < r < msg.range_max]
        
        if valid_front:
            min_front = min(valid_front)
            
            if min_front < self.safe_distance:
                # OBSTACLE! Stop and turn
                cmd.linear.x = 0.0
                cmd.angular.z = 0.5  # Turn left
                self.get_logger().warn('Avoiding obstacle!')
            else:
                # Clear ahead - move forward
                cmd.linear.x = 0.2
                cmd.angular.z = 0.0
        
        self.cmd_pub.publish(cmd)
```

---

## 💻 Exercises

### Exercise 9.1: Minimum Distance Finder

Create a node that continuously reports the closest obstacle distance and angle.

```python
# Your task:
# 1. Subscribe to /scan
# 2. Find minimum valid distance
# 3. Calculate its angle
# 4. Publish to custom topic or log every second
```

### Exercise 9.2: 4-Direction Monitor

Create a node that divides the scan into 4 quadrants (front, left, back, right) and reports the minimum distance in each.

### Exercise 9.3: Wall Follower

Create a simple wall-following robot:
- Keep right side at 0.5m from wall
- If closer: turn left
- If farther: turn right
- Move forward at constant speed

---

## 🔧 LiDAR in Gazebo

Your robot already has LiDAR if you followed Chapter 7!

**Check it**:
```bash
# Launch robot
ros2 launch my_robot_description gazebo.launch.py

# Check topic
ros2 topic list | grep scan
# Should see: /scan

# See data
ros2 topic echo /scan --once
```

**URDF configuration** (from Chapter 6):
```xml
<gazebo reference="lidar_link">
  <sensor name="lidar" type="ray">
    <always_on>true</always_on>
    <update_rate>10</update_rate>
    <visualize>false</visualize>
    <ray>
      <scan>
        <horizontal>
          <samples>360</samples>
          <resolution>1</resolution>
          <min_angle>-3.14159</min_angle>
          <max_angle>3.14159</max_angle>
        </horizontal>
      </scan>
      <range>
        <min>0.15</min>
        <max>12.0</max>
      </range>
    </ray>
    <plugin name="scan" filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <remapping>~/out:=scan</remapping>
      </ros>
      <output_type>sensor_msgs/LaserScan</output_type>
      <frame_name>lidar_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

---

## 📊 Understanding Scan Parameters

**360 samples in 360° scan**:
- `angle_min = -π` (-180°)
- `angle_max = +π` (+180°)
- `angle_increment = 2π / 360 ≈ 0.0175` (1°)
- Index 0 = back
- Index 180 = front
- Index 90 = left
- Index 270 = right

**Converting angle to index**:
```python
index = int((desired_angle - msg.angle_min) / msg.angle_increment)
```

**Converting index to angle**:
```python
angle = msg.angle_min + index * msg.angle_increment
```

---

## 🐛 Common Issues

### No /scan topic
- Is LiDAR in your URDF?
- Is Gazebo sensor plugin configured?
- Check: `ros2 topic list`

### All ranges are `inf`
- LiDAR might be inside robot body
- Check `<origin>` in URDF
- Make sure it's above/outside collision geometry

### Readings seem backwards
- LiDAR coordinate frame might be rotated
- Check TF tree: `ros2 run tf2_tools view_frames`
- Adjust `<origin rpy="...">` in URDF

---

## 🎯 Key Takeaways

1. **LaserScan message** contains array of distance measurements
2. **Angles** map to array indices via `angle_min` + `index * angle_increment`
3. **Filter invalid readings**: `inf`, `nan`, or outside `range_min`/`range_max`
4. **Sector analysis** checks angular ranges for obstacles
5. **RViz visualization** helps debug LiDAR data
6. **Reactive behaviors** use LiDAR for real-time obstacle avoidance

---

## 🚀 Next Chapter

[Chapter 10: Custom Messages](../chapter_10_custom_messages/README.md) - Create your own message types for robot-specific data!

---

## 📚 Resources

- [sensor_msgs/LaserScan](https://docs.ros.org/en/jazzy/p/sensor_msgs/interfaces/msg/LaserScan.html)
- [Gazebo LiDAR Plugin](http://gazebosim.org/tutorials?tut=ros2_installing&cat=connect_ros#Lidar)
- [RViz LaserScan Display](https://github.com/ros2/rviz/blob/jazzy/rviz_default_plugins/docs/LaserScan.md)
