# Chapter 13: Map Management & Localization

**Goal**: Save, load, and use maps for navigation!

---

## 📖 Map Files

After SLAM creates a map, you need to save it for navigation.

**Two types of map files**:

### 1. Image Map (for Nav2)
- `.pgm` file (image)
- `.yaml` file (metadata)
- Used by `map_server` and Nav2

### 2. Pose Graph (for slam_toolbox)
- `.posegraph` file
- Contains full SLAM state
- Can continue mapping later

---

## 💾 Saving Maps

### Method 1: map_saver_cli (Nav2)

```bash
# Save current map to files
ros2 run nav2_map_server map_saver_cli -f my_map

# Creates:
# - my_map.pgm (grayscale image)
# - my_map.yaml (metadata)
```

**Options**:
```bash
# Save to specific directory
ros2 run nav2_map_server map_saver_cli -f ~/maps/living_room

# Specify map topic
ros2 run nav2_map_server map_saver_cli -f my_map --ros-args -r map:=/custom_map_topic
```

---

### Method 2: slam_toolbox Serialization

```bash
# Save pose graph (full SLAM state)
ros2 service call /slam_toolbox/serialize_map \
  slam_toolbox/srv/SerializePoseGraph \
  "{filename: '/home/user/maps/my_slam_map'}"

# Creates: my_slam_map.posegraph
```

**Advantages**:
- Can continue mapping later
- Preserves full optimization state
- Better for iterative mapping

---

## 📄 Map YAML File

Example `my_map.yaml`:

```yaml
image: my_map.pgm
resolution: 0.050000  # meters per pixel
origin: [-10.0, -10.0, 0.0]  # [x, y, yaw] of pixel (0,0)
occupied_thresh: 0.65  # Probability threshold for occupied
free_thresh: 0.25      # Probability threshold for free
negate: 0              # Whether to invert black/white
mode: trinary          # trinary, scale, or raw
```

---

## 🗺️ Loading Maps with map_server

### Launch File Method

```python
import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Get map file path
    map_file = os.path.join(
        get_package_share_directory('my_robot_navigation'),
        'maps',
        'my_map.yaml')
    
    return LaunchDescription([
        # Map server
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[
                {'yaml_filename': map_file},
                {'use_sim_time': True}
            ]
        ),
        
        # Lifecycle manager (activates map_server)
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_mapper',
            output='screen',
            parameters=[
                {'node_names': ['map_server']},
                {'autostart': True}
            ]
        )
    ])
```

---

### Command Line Method

```bash
# Start map server
ros2 run nav2_map_server map_server --ros-args \
  -p yaml_filename:=/path/to/my_map.yaml \
  -p use_sim_time:=true

# In another terminal, activate it
ros2 lifecycle set /map_server configure
ros2 lifecycle set /map_server activate
```

---

## 🎯 AMCL: Adaptive Monte Carlo Localization

**AMCL** localizes robot on a known map using particle filter.

### Install

```bash
sudo apt install ros-jazzy-nav2-amcl
```

---

### Basic AMCL Launch

```python
Node(
    package='nav2_amcl',
    executable='amcl',
    name='amcl',
    output='screen',
    parameters=[{
        'use_sim_time': True,
        'alpha1': 0.2,  # Rotation noise from rotation
        'alpha2': 0.2,  # Rotation noise from translation
        'alpha3': 0.2,  # Translation noise from translation
        'alpha4': 0.2,  # Translation noise from rotation
        'base_frame_id': 'base_link',
        'global_frame_id': 'map',
        'odom_frame_id': 'odom',
        'scan_topic': 'scan',
        'max_particles': 2000,
        'min_particles': 500,
    }]
),
```

---

### AMCL Parameters Explained

```yaml
amcl:
  ros__parameters:
    # Frame IDs
    base_frame_id: "base_link"
    odom_frame_id: "odom"
    global_frame_id: "map"
    
    # Topics
    scan_topic: "scan"
    
    # Particle filter
    max_particles: 2000
    min_particles: 500
    
    # Odometry model noise
    alpha1: 0.2  # Expected rotation noise per rotation
    alpha2: 0.2  # Expected rotation noise per translation
    alpha3: 0.2  # Expected translation noise per translation
    alpha4: 0.2  # Expected translation noise per rotation
    
    # Laser model
    laser_model_type: "likelihood_field"
    laser_likelihood_max_dist: 2.0
    laser_max_range: 12.0
    laser_min_range: 0.15
    
    # Update thresholds
    update_min_d: 0.2   # Minimum translation before update (m)
    update_min_a: 0.5   # Minimum rotation before update (rad)
    
    # Transform publishing
    transform_tolerance: 1.0
    
    # Initial pose
    set_initial_pose: false
    initial_pose:
      x: 0.0
      y: 0.0
      z: 0.0
      yaw: 0.0
```

---

## 🎯 Setting Initial Pose

### Method 1: RViz

1. Open RViz
2. Click "2D Pose Estimate" button
3. Click and drag on map to set pose
4. Publishes to `/initialpose`

---

### Method 2: Programmatically

```python
from geometry_msgs.msg import PoseWithCovarianceStamped

class InitialPosePublisher(Node):
    def __init__(self):
        super().__init__('initial_pose_publisher')
        
        self.publisher = self.create_publisher(
            PoseWithCovarianceStamped,
            '/initialpose',
            10)
        
        # Wait for AMCL to be ready
        self.timer = self.create_timer(2.0, self.publish_initial_pose)
    
    def publish_initial_pose(self):
        """Set robot's initial pose on map."""
        msg = PoseWithCovarianceStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'map'
        
        # Position
        msg.pose.pose.position.x = 0.0
        msg.pose.pose.position.y = 0.0
        msg.pose.pose.position.z = 0.0
        
        # Orientation (quaternion)
        msg.pose.pose.orientation.x = 0.0
        msg.pose.pose.orientation.y = 0.0
        msg.pose.pose.orientation.z = 0.0
        msg.pose.pose.orientation.w = 1.0
        
        # Covariance (uncertainty)
        msg.pose.covariance = [0.25, 0.0, 0.0, 0.0, 0.0, 0.0,
                               0.0, 0.25, 0.0, 0.0, 0.0, 0.0,
                               0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                               0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                               0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                               0.0, 0.0, 0.0, 0.0, 0.0, 0.06]
        
        self.publisher.publish(msg)
        self.get_logger().info('Initial pose set!')
        self.timer.cancel()
```

---

## 📊 Complete Localization System

### Launch File: localization.launch.py

```python
import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    map_file = LaunchConfiguration('map')
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time'),
        
        DeclareLaunchArgument(
            'map',
            default_value='/path/to/my_map.yaml',
            description='Full path to map yaml file'),
        
        # Map Server
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[
                {'yaml_filename': map_file},
                {'use_sim_time': use_sim_time}
            ]
        ),
        
        # AMCL
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'base_frame_id': 'base_link',
                'odom_frame_id': 'odom',
                'global_frame_id': 'map',
                'scan_topic': 'scan',
            }]
        ),
        
        # Lifecycle Manager
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[
                {'node_names': ['map_server', 'amcl']},
                {'autostart': True},
                {'use_sim_time': use_sim_time}
            ]
        ),
    ])
```

---

## 🔧 Map Editing

### Method 1: GIMP

```bash
# Install GIMP
sudo apt install gimp

# Open map
gimp my_map.pgm

# Edit:
# - White = free space
# - Black = walls
# - Gray = unknown

# Save as .pgm
```

---

### Method 2: Python (Programmatic)

```python
from PIL import Image
import yaml

# Load map
img = Image.open('my_map.pgm')
pixels = img.load()

# Edit pixels
width, height = img.size
for x in range(width):
    for y in range(height):
        # Example: Fill region with free space
        if 100 < x < 200 and 100 < y < 200:
            pixels[x, y] = 255  # White = free

# Save
img.save('my_map_edited.pgm')

# Update YAML to point to new file
with open('my_map.yaml', 'r') as f:
    data = yaml.safe_load(f)

data['image'] = 'my_map_edited.pgm'

with open('my_map_edited.yaml', 'w') as f:
    yaml.dump(data, f)
```

---

## 🗂️ Organizing Maps

```
my_robot_navigation/
├── maps/
│   ├── home/
│   │   ├── home.pgm
│   │   └── home.yaml
│   ├── office/
│   │   ├── office.pgm
│   │   └── office.yaml
│   └── warehouse/
│       ├── warehouse.pgm
│       └── warehouse.yaml
├── config/
│   ├── amcl_config.yaml
│   └── map_server_config.yaml
└── launch/
    └── localization.launch.py
```

---

## 💻 Exercise: Multi-Map System

Create a service to switch between maps:

```python
from my_robot_interfaces.srv import LoadMap

class MapManager(Node):
    def __init__(self):
        super().__init__('map_manager')
        
        self.maps = {
            'home': '/path/to/home.yaml',
            'office': '/path/to/office.yaml',
        }
        
        self.srv = self.create_service(
            LoadMap,
            '/load_map',
            self.load_map_callback)
        
        self.map_client = self.create_client(
            LifecycleNodes,
            '/map_server/change_state')
    
    def load_map_callback(self, request, response):
        """Load a different map."""
        map_name = request.map_name
        
        if map_name in self.maps:
            # Deactivate current map_server
            # Configure with new map
            # Activate
            response.success = True
            response.message = f"Loaded {map_name}"
        else:
            response.success = False
            response.message = f"Unknown map: {map_name}"
        
        return response
```

---

## 🐛 Troubleshooting

### Map not loading
```bash
# Check map_server is running
ros2 node list | grep map_server

# Check lifecycle state
ros2 lifecycle get /map_server

# Activate if needed
ros2 lifecycle set /map_server configure
ros2 lifecycle set /map_server activate
```

### AMCL not localizing
- Set initial pose in RViz
- Check particle cloud: `rostopic echo /particlecloud`
- Increase `max_particles`
- Drive robot around to disperse particles

### TF errors
- Ensure map_server and AMCL running
- Check TF tree: `ros2 run tf2_tools view_frames`
- Should see: `map` → `odom` → `base_link`

---

## 🎯 Key Takeaways

1. **Save maps** with `map_saver_cli`
2. **map_server** serves maps to navigation stack
3. **AMCL** localizes robot on known map
4. **Initial pose** helps AMCL converge faster
5. **Edit maps** with GIMP or programmatically
6. **Lifecycle management** activates nodes

---

## 🚀 Next Chapter

[Chapter 15: Path Planning](../chapter_15_path_planning/README.md) - Plan collision-free paths on your maps!

---

## 📚 Resources

- [map_server Documentation](https://docs.nav2.org/configuration/packages/configuring-map-server.html)
- [AMCL Documentation](https://docs.nav2.org/configuration/packages/configuring-amcl.html)
- [Nav2 Tutorials](https://docs.nav2.org/tutorials/index.html)
