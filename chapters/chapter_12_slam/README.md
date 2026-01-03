# Chapter 12: Implementing SLAM with slam_toolbox

**Goal**: Build maps of your environment using SLAM (Simultaneous Localization and Mapping)!

---

## 📖 What is SLAM?

**SLAM** solves two problems at once:
1. **Localization**: Where am I?
2. **Mapping**: What does the environment look like?

```
Robot doesn't know:
- Its position
- The map

After SLAM:
- Knows its position on map
- Has built a map of environment
```

**Why is this hard?**
- To know position, you need a map
- To build a map, you need to know your position
- SLAM does both simultaneously!

---

## 🛠️ slam_toolbox

**slam_toolbox** is the recommended SLAM package for ROS2.

**Features**:
- 2D LiDAR-based mapping
- Graph-based optimization
- Online (real-time) and offline mapping
- Map saving/loading
- Localization mode

**Install**:
```bash
sudo apt install ros-jazzy-slam-toolbox
```

---

## 🚀 Quick Start: Mapping Mode

### Step 1: Launch Your Robot

```bash
# Start robot in Gazebo
ros2 launch my_robot_description gazebo.launch.py
```

**Requirements**:
- `/scan` topic (LiDAR)
- `/odom` topic (odometry)
- TF tree (`odom` → `base_link`)

---

### Step 2: Launch SLAM Toolbox

```bash
# Online async mapping mode
ros2 launch slam_toolbox online_async_launch.py
```

---

### Step 3: Visualize in RViz

```bash
rviz2
```

**RViz setup**:
1. Fixed Frame: `map`
2. Add → Map → Topic: `/map`
3. Add → LaserScan → Topic: `/scan`
4. Add → TF

You should see the map being built in real-time!

---

### Step 4: Drive Robot to Build Map

```bash
# Teleop
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

**Tips**:
- Drive slowly for better accuracy
- Cover all areas you want mapped
- Loop closures improve map quality

---

### Step 5: Save Map

```bash
# Save map files
ros2 run nav2_map_server map_saver_cli -f my_map

# Creates:
# - my_map.pgm (image)
# - my_map.yaml (metadata)
```

Also save SLAM pose graph:

```bash
# Call service to serialize map
ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph "{filename: '/home/user/my_slam_map'}"
```

---

## ⚙️ Configuration

### Create Custom Config

Create `config/mapper_params_online_async.yaml`:

```yaml
slam_toolbox:
  ros__parameters:
    # Plugin params
    solver_plugin: solver_plugins::CeresSolver
    ceres_linear_solver: SPARSE_NORMAL_CHOLESKY
    ceres_preconditioner: SCHUR_JACOBI
    ceres_trust_strategy: LEVENBERG_MARQUARDT
    ceres_dogleg_type: TRADITIONAL_DOGLEG
    ceres_loss_function: None

    # ROS Parameters
    odom_frame: odom
    map_frame: map
    base_frame: base_link
    scan_topic: /scan
    mode: mapping  # or localization

    # Lifelong params
    map_file_name: ""
    map_start_pose: [0.0, 0.0, 0.0]
    map_start_at_dock: true

    debug_logging: false
    throttle_scans: 1
    transform_publish_period: 0.02  # 50 Hz
    map_update_interval: 5.0
    resolution: 0.05
    max_laser_range: 12.0  # meters
    minimum_time_interval: 0.5
    transform_timeout: 0.2
    tf_buffer_duration: 30.0
    stack_size_to_use: 40000000  # bytes

    # General Parameters
    use_scan_matching: true
    use_scan_barycenter: true
    minimum_travel_distance: 0.5  # meters
    minimum_travel_heading: 0.5  # radians
    scan_buffer_size: 10
    scan_buffer_maximum_scan_distance: 10.0
    link_match_minimum_response_fine: 0.1  
    link_scan_maximum_distance: 1.5
    loop_search_maximum_distance: 3.0
    do_loop_closing: true 
    loop_match_minimum_chain_size: 10           
    loop_match_maximum_variance_coarse: 3.0  
    loop_match_minimum_response_coarse: 0.35    
    loop_match_minimum_response_fine: 0.45

    # Correlation Parameters - Correlation Parameters
    correlation_search_space_dimension: 0.5
    correlation_search_space_resolution: 0.01
    correlation_search_space_smear_deviation: 0.1 

    # Scan Matcher Parameters
    coarse_search_angle_offset: 0.349     
    coarse_angle_resolution: 0.0349        
    minimum_angle_penalty: 0.9
    minimum_distance_penalty: 0.5
    use_response_expansion: true
```

---

### Launch with Custom Config

Create `launch/online_async_launch.py`:

```python
import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Get config file
    slam_params_file = os.path.join(
        get_package_share_directory('my_robot_slam'),
        'config',
        'mapper_params_online_async.yaml')

    return LaunchDescription([
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[slam_params_file],
        )
    ])
```

---

## 🗺️ Understanding the Map

### Map Message: nav_msgs/OccupancyGrid

```python
std_msgs/Header header
nav_msgs/MapMetaData info
  time map_load_time
  float32 resolution        # meters/pixel
  uint32 width             # pixels
  uint32 height            # pixels
  geometry_msgs/Pose origin
int8[] data  # 0-100 or -1
```

**Cell values**:
- `0` = Free (white)
- `100` = Occupied (black)
- `-1` = Unknown (gray)

---

## 🔄 Mapping Modes

### 1. Online Async (Default)

- Real-time mapping
- Asynchronous processing
- Best for live robots

```bash
ros2 launch slam_toolbox online_async_launch.py
```

---

### 2. Online Sync

- Real-time mapping
- Synchronous (waits for each scan)
- More accurate but slower

```bash
ros2 launch slam_toolbox online_sync_launch.py
```

---

### 3. Offline

- Process pre-recorded bag files
- Not real-time
- Best quality

```bash
# Record data first
ros2 bag record /scan /tf /tf_static /odom

# Then process
ros2 launch slam_toolbox offline_launch.py
```

---

## 📍 Localization Mode

After building a map, use it for localization only:

### Step 1: Create Localization Config

`config/mapper_params_localization.yaml`:

```yaml
slam_toolbox:
  ros__parameters:
    mode: localization  # Key change!
    
    # Load existing map
    map_file_name: /path/to/my_slam_map
    map_start_pose: [0.0, 0.0, 0.0]
    
    # ... (rest same as mapping config)
```

---

### Step 2: Launch

```python
# Launch file for localization
Node(
    package='slam_toolbox',
    executable='localization_slam_toolbox_node',
    name='slam_toolbox',
    output='screen',
    parameters=[localization_params_file],
)
```

---

## 🎯 Key Topics

| Topic | Type | Description |
|-------|------|-------------|
| `/scan` | LaserScan | Input LiDAR data |
| `/map` | OccupancyGrid | Output map |
| `/odom` | Odometry | Wheel odometry |
| `/tf` | TFMessage | Transform tree |

---

## 🛠️ Key Services

```bash
# Save map
ros2 service call /slam_toolbox/serialize_map \
  slam_toolbox/srv/SerializePoseGraph \
  "{filename: '/path/to/map'}"

# Load map
ros2 service call /slam_toolbox/deserialize_map \
  slam_toolbox/srv/DeserializePoseGraph \
  "{filename: '/path/to/map'}"

# Pause/resume
ros2 service call /slam_toolbox/pause_new_measurements \
  slam_toolbox/srv/Pause
```

---

## 💻 Programmatic Map Access

### Subscribe to Map

```python
from nav_msgs.msg import OccupancyGrid

class MapSubscriber(Node):
    def __init__(self):
        super().__init__('map_subscriber')
        
        self.subscription = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.map_callback,
            10)
        
        self.map = None
    
    def map_callback(self, msg):
        """Receive updated map."""
        self.map = msg
        
        self.get_logger().info(
            f'Received map: {msg.info.width}x{msg.info.height} @ '
            f'{msg.info.resolution}m/pixel')
        
        # Count cell types
        free = sum(1 for cell in msg.data if cell == 0)
        occupied = sum(1 for cell in msg.data if cell == 100)
        unknown = sum(1 for cell in msg.data if cell == -1)
        
        self.get_logger().info(
            f'Free: {free}, Occupied: {occupied}, Unknown: {unknown}')
```

---

## 🔍 Map Coordinate Conversion

```python
def world_to_map(self, x_world, y_world, map_msg):
    """Convert world coordinates to map pixel coordinates."""
    # Get origin
    origin_x = map_msg.info.origin.position.x
    origin_y = map_msg.info.origin.position.y
    resolution = map_msg.info.resolution
    
    # Convert
    map_x = int((x_world - origin_x) / resolution)
    map_y = int((y_world - origin_y) / resolution)
    
    return map_x, map_y

def map_to_world(self, map_x, map_y, map_msg):
    """Convert map pixel coordinates to world coordinates."""
    origin_x = map_msg.info.origin.position.x
    origin_y = map_msg.info.origin.position.y
    resolution = map_msg.info.resolution
    
    world_x = map_x * resolution + origin_x
    world_y = map_y * resolution + origin_y
    
    return world_x, world_y

def get_cell_value(self, x_world, y_world, map_msg):
    """Get occupancy value at world coordinate."""
    map_x, map_y = self.world_to_map(x_world, y_world, map_msg)
    
    # Check bounds
    if not (0 <= map_x < map_msg.info.width and 
            0 <= map_y < map_msg.info.height):
        return -1  # Out of bounds
    
    # Get index
    index = map_y * map_msg.info.width + map_x
    
    return map_msg.data[index]
```

---

## 📊 Tuning Parameters

### For Better Accuracy

```yaml
resolution: 0.02  # Smaller = more detail
minimum_travel_distance: 0.3  # Update more often
do_loop_closing: true  # Improve consistency
```

### For Faster Performance

```yaml
resolution: 0.10  # Larger = faster
throttle_scans: 2  # Process fewer scans
minimum_travel_distance: 1.0  # Update less often
```

### For Large Environments

```yaml
stack_size_to_use: 80000000  # More memory
loop_search_maximum_distance: 5.0  # Larger loop search
```

---

## 🐛 Troubleshooting

### Map not building
- Check `/scan` topic: `ros2 topic echo /scan`
- Check TF tree: `ros2 run tf2_tools view_frames`
- Verify `odom` → `base_link` transform exists

### Map drifting
- Improve wheel odometry
- Drive slower
- Enable loop closure
- Check laser alignment

### Poor loop closures
- Increase `loop_match_minimum_chain_size`
- Adjust `loop_search_maximum_distance`
- Ensure environment has features

---

## 💻 Complete Example Launch

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
import os


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time'),
        
        # Robot in Gazebo
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=['-entity', 'my_robot', 
                      '-topic', 'robot_description'],
        ),
        
        # SLAM Toolbox
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            parameters=[
                {'use_sim_time': use_sim_time},
                {'slam_toolbox': {
                    'odom_frame': 'odom',
                    'map_frame': 'map',
                    'base_frame': 'base_link',
                    'scan_topic': '/scan',
                    'mode': 'mapping',
                }}
            ],
            output='screen',
        ),
        
        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', '/path/to/slam.rviz'],
        ),
    ])
```

---

## 🎯 Key Takeaways

1. **slam_toolbox** builds 2D maps from LiDAR
2. **Mapping mode** creates new maps
3. **Localization mode** uses existing maps
4. **Loop closure** improves map consistency
5. **Save maps** for reuse with Nav2
6. **Tune parameters** for your environment

---

## 🚀 Next Chapter

[Chapter 13: Map Management](../chapter_13_maps/README.md) - Save, load, and edit maps!

---

## 📚 Resources

- [slam_toolbox GitHub](https://github.com/SteveMacenski/slam_toolbox)
- [slam_toolbox Documentation](https://github.com/SteveMacenski/slam_toolbox/blob/ros2/README.md)
- [Tuning Guide](https://github.com/SteveMacenski/slam_toolbox/blob/ros2/docs/Tuning.md)
