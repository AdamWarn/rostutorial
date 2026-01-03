# Chapter 19: Performance Optimization & Debugging

**Goal**: Make your robot faster, more reliable, and easier to debug!

---

## 📖 Why Optimize?

**Problems with unoptimized robots**:
- Slow reactions
- High CPU/memory usage
- Battery drains quickly
- Navigation failures

**After optimization**:
- Faster response
- Efficient resource use
- Longer battery life
- Reliable operation

---

## 🎯 Understanding Performance Basics

### What Uses Resources?

**CPU (Processor)**: Doing calculations
- Path planning
- SLAM processing
- Sensor data processing

**Memory (RAM)**: Storing data
- Maps
- Scan history
- Buffers

**Network (Bandwidth)**: Sending data
- Large images
- Point clouds
- High-frequency messages

---

## 📊 Monitoring Performance

### Using `htop` (System Monitor)

```bash
# Install htop
sudo apt install htop

# Run it
htop
```

**What to look for**:
- **CPU%**: Should stay under 80% average
- **MEM%**: Should have some free memory
- **Load average**: Should be below number of CPU cores

---

### ROS2 Tools

#### Check Node CPU Usage

```bash
# List all nodes
ros2 node list

# Get info about a node
ros2 node info /slam_toolbox

# Monitor topic frequency
ros2 topic hz /scan

# Check topic bandwidth
ros2 topic bw /scan
```

---

#### Monitor Topic Rates

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import time


class TopicMonitor(Node):
    """
    Monitor how fast messages arrive.
    
    This helps you see if publishers are too fast or too slow.
    """
    
    def __init__(self):
        super().__init__('topic_monitor')
        
        # Counter and timer
        self.msg_count = 0
        self.start_time = time.time()
        
        # Subscribe to topic
        self.create_subscription(
            LaserScan,
            '/scan',
            self.callback,
            10)
        
        # Print stats every 5 seconds
        self.create_timer(5.0, self.print_stats)
    
    def callback(self, msg):
        """Count each message."""
        self.msg_count += 1
    
    def print_stats(self):
        """Calculate and print frequency."""
        elapsed = time.time() - self.start_time
        frequency = self.msg_count / elapsed
        
        self.get_logger().info(
            f'Messages: {self.msg_count} | '
            f'Frequency: {frequency:.2f} Hz')
        
        # Reset
        self.msg_count = 0
        self.start_time = time.time()


def main():
    rclpy.init()
    node = TopicMonitor()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

## ⚡ Optimization Techniques

### 1. Reduce Publishing Rate

**Problem**: Publishing too fast wastes resources

```python
# ❌ Too fast (100Hz) for status updates
self.create_timer(0.01, self.publish_status)

# ✅ Reasonable (1Hz) for status
self.create_timer(1.0, self.publish_status)
```

**Guidelines**:
- **Robot odometry**: 20-50 Hz
- **Sensor data (LiDAR)**: 10-20 Hz
- **Status messages**: 1-5 Hz
- **Diagnostics**: 0.1-1 Hz

---

### 2. Use Appropriate QoS Settings

**QoS** = Quality of Service (how reliable messages are)

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

# For sensor data (OK to miss some messages)
sensor_qos = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,  # Fast, may drop
    history=HistoryPolicy.KEEP_LAST,
    depth=1  # Only keep latest
)

publisher = self.create_publisher(
    LaserScan,
    '/scan',
    sensor_qos)  # Use custom QoS

# For critical commands (must receive all)
reliable_qos = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,  # Slower, guaranteed
    history=HistoryPolicy.KEEP_LAST,
    depth=10
)
```

---

### 3. Optimize Message Size

**Problem**: Large messages use bandwidth

```python
# ❌ Sending full map every second (huge!)
map_pub.publish(full_map)  # 10MB message!

# ✅ Only send map when it changes
if map_changed:
    map_pub.publish(updated_map)

# ✅ Or compress the data
compressed_map = compress(full_map)
compressed_pub.publish(compressed_map)
```

---

### 4. Throttle Logs

```python
# ❌ Logs spam the console
self.get_logger().info('Position updated')  # Called 50 times/sec!

# ✅ Throttled logging
self.get_logger().info(
    'Position updated',
    throttle_duration_sec=5.0)  # Only every 5 seconds
```

---

## 🐛 Debugging Tools

### 1. ros2 bag (Record & Replay)

**Record data** for later analysis:

```bash
# Record specific topics
ros2 bag record /scan /odom /tf

# Record all topics
ros2 bag record -a

# Record for specific time
ros2 bag record /scan --duration 60  # 60 seconds

# Record to specific folder
ros2 bag record -o my_test_run /scan /cmd_vel
```

**Replay data**:

```bash
# Play recorded data
ros2 bag play my_test_run

# Play at half speed (for analysis)
ros2 bag play my_test_run --rate 0.5

# Loop playback
ros2 bag play my_test_run --loop
```

**Why this is useful**:
- Test without robot
- Reproduce bugs
- Analyze failures
- Share data with others

---

### 2. rqt (Visual Tools)

```bash
# Install rqt
sudo apt install ros-jazzy-rqt ros-jazzy-rqt-common-plugins

# Run rqt
rqt
```

**Useful plugins**:

**rqt_graph**: See node connections
```bash
rqt_graph
```

**rqt_plot**: Plot numeric data
```bash
rqt_plot /odom/pose/pose/position/x /odom/pose/pose/position/y
```

**rqt_console**: See all log messages
```bash
rqt_console
```

**rqt_topic**: Monitor topics
```bash
rqt_topic
```

---

### 3. Launch File Debugging

**Add logging levels**:

```python
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration

Node(
    package='my_package',
    executable='my_node',
    name='my_node',
    output='screen',  # Show output
    arguments=['--ros-args', '--log-level', 'DEBUG'],  # More details
    emulate_tty=True,  # Better formatting
)
```

---

### 4. Python Debugging with print()

```python
class DebugNode(Node):
    def callback(self, msg):
        # Quick debugging with print
        print(f"DEBUG: Received message: {msg.data}")
        
        # Or use logger with levels
        self.get_logger().debug(f"Details: {msg}")
        self.get_logger().info(f"Info: {msg}")
        self.get_logger().warn(f"Warning: {msg}")
        self.get_logger().error(f"Error: {msg}")
```

**Set log level**:
```bash
# See debug messages
ros2 run my_package my_node --ros-args --log-level DEBUG
```

---

## 📈 Profiling (Finding Slow Code)

### Using Python's cProfile

```python
import cProfile
import pstats

def slow_function():
    """Example function that might be slow."""
    total = 0
    for i in range(1000000):
        total += i
    return total

# Profile the function
profiler = cProfile.Profile()
profiler.enable()

slow_function()  # Run your code

profiler.disable()

# Print results
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 slowest
```

**In ROS2 node**:

```python
import cProfile

class ProfiledNode(Node):
    def __init__(self):
        super().__init__('profiled_node')
        
        # Start profiler
        self.profiler = cProfile.Profile()
        self.profiler.enable()
        
        # Your normal init code...
    
    def __del__(self):
        # Stop profiler when node ends
        self.profiler.disable()
        self.profiler.dump_stats('node_profile.prof')
        print("Profile saved to node_profile.prof")
```

**Analyze results**:
```bash
# Install snakeviz (visual profiler)
pip3 install snakeviz

# Visualize profile
snakeviz node_profile.prof
```

---

## 🔧 Parameter Tuning

### Nav2 Performance Tuning

**For faster planning**:
```yaml
planner_server:
  ros__parameters:
    expected_planner_frequency: 20.0  # Plan more often
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.5  # Larger = faster but less precise
      use_astar: true  # A* faster than Dijkstra
```

**For better obstacle avoidance**:
```yaml
controller_server:
  ros__parameters:
    controller_frequency: 20.0  # Update more often
    FollowPath:
      sim_time: 1.7  # Look ahead time
      vx_samples: 20  # More samples = smoother but slower
      vth_samples: 40
```

---

### SLAM Performance Tuning

```yaml
slam_toolbox:
  ros__parameters:
    # Faster (less accurate)
    throttle_scans: 2  # Process every 2nd scan
    resolution: 0.10   # Larger cells
    
    # Slower (more accurate)
    throttle_scans: 1
    resolution: 0.05
```

---

## 💻 Memory Management

### Monitor Memory Usage

```python
import psutil  # pip3 install psutil

class MemoryMonitor(Node):
    def __init__(self):
        super().__init__('memory_monitor')
        
        # Check memory every 10 seconds
        self.create_timer(10.0, self.check_memory)
    
    def check_memory(self):
        """Log current memory usage."""
        # Get process info
        process = psutil.Process()
        mem_info = process.memory_info()
        
        # Convert to MB
        mem_mb = mem_info.rss / 1024 / 1024
        
        # Get system memory
        sys_mem = psutil.virtual_memory()
        
        self.get_logger().info(
            f'Node memory: {mem_mb:.1f} MB | '
            f'System: {sys_mem.percent}% used')
        
        # Warn if high
        if mem_mb > 500:  # 500 MB
            self.get_logger().warn('High memory usage!')
```

---

### Limit Buffer Sizes

```python
# ❌ Unlimited buffer (memory leak risk)
self.scan_history = []

def callback(self, msg):
    self.scan_history.append(msg)  # Grows forever!

# ✅ Fixed-size buffer
from collections import deque

self.scan_history = deque(maxlen=10)  # Keep only last 10

def callback(self, msg):
    self.scan_history.append(msg)  # Auto-removes oldest
```

---

## 🎯 Common Performance Issues

### Issue 1: TF Lookup Timeout

**Symptom**: "Could not transform" errors

**Fix**:
```python
# ❌ No timeout
trans = buffer.lookup_transform('map', 'base_link', rclpy.time.Time())

# ✅ With timeout
from rclpy.duration import Duration

trans = buffer.lookup_transform(
    'map', 'base_link',
    rclpy.time.Time(),
    timeout=Duration(seconds=1.0))  # Wait up to 1 second
```

---

### Issue 2: Slow Callbacks

**Symptom**: Messages backing up, delayed reactions

**Fix**: Don't do heavy work in callbacks

```python
# ❌ Slow callback blocks everything
def scan_callback(self, msg):
    processed = heavy_processing(msg)  # Takes 1 second!
    self.publisher.publish(processed)

# ✅ Use threading for heavy work
import threading

def scan_callback(self, msg):
    # Quick: start processing in background
    thread = threading.Thread(
        target=self.process_scan,
        args=(msg,))
    thread.start()

def process_scan(self, msg):
    # Heavy work happens here without blocking
    processed = heavy_processing(msg)
    self.publisher.publish(processed)
```

---

### Issue 3: Too Many Topics

**Symptom**: Network congestion

**Fix**: Combine related data

```python
# ❌ Many separate topics
self.pub_x = self.create_publisher(Float32, '/robot/x', 10)
self.pub_y = self.create_publisher(Float32, '/robot/y', 10)
self.pub_yaw = self.create_publisher(Float32, '/robot/yaw', 10)

# ✅ One combined topic
from geometry_msgs.msg import Pose2D

self.pub_pose = self.create_publisher(Pose2D, '/robot/pose', 10)
```

---

## 💻 Exercises

### Exercise 19.1: Profile Your Node

1. Create a node with a callback
2. Profile it with cProfile
3. Find the slowest part
4. Optimize it

### Exercise 19.2: Monitor System Resources

Create a node that:
- Monitors CPU%
- Monitors memory
- Publishes warnings if too high

### Exercise 19.3: Record & Replay

1. Record 1 minute of /scan and /odom
2. Play it back
3. Test your algorithm with recorded data

---

## 🎯 Key Takeaways

1. **Monitor** CPU, memory, and network usage
2. **Profile** to find slow code
3. **Throttle** high-frequency publishers
4. **ros2 bag** records data for debugging
5. **rqt tools** visualize system state
6. **Tune parameters** for performance vs accuracy
7. **Fix memory leaks** with limited buffers

---

## 🚀 Next Chapter

[Chapter 20: Hardware Integration](../chapter_20_hardware/README.md) - Connect real sensors and motors!

---

## 📚 Resources

- [ROS2 Performance](https://docs.ros.org/en/jazzy/Concepts/About-Quality-of-Service-Settings.html)
- [rqt Tools](https://docs.ros.org/en/jazzy/Concepts/About-RQt.html)
- [ros2 bag](https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Recording-And-Playing-Back-Data/Recording-And-Playing-Back-Data.html)
- [Python Profiling](https://docs.python.org/3/library/profile.html)
