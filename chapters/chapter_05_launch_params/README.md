# Chapter 5: Launch Files & Parameters

**Goal**: Learn to start multiple nodes together and configure them with parameters.

---

## 📖 What are Launch Files?

Instead of opening 10 terminals to start 10 nodes, use a **launch file**!

**Benefits:**
- Start multiple nodes with one command
- Set parameters
- Remap topics
- Configure namespaces
- Set environment variables

---

## 🎯 Python Launch Files (ROS2 Standard)

**File**: `~/ros2_ws/src/my_first_pkg/launch/my_launch.launch.py`

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Start publisher
        Node(
            package='my_first_pkg',
            executable='simple_publisher',
            name='publisher_node',
            output='screen'
        ),
        
        # Start subscriber
        Node(
            package='my_first_pkg',
            executable='simple_subscriber',
            name='subscriber_node',
            output='screen'
        ),
    ])
```

**Run it:**
```bash
ros2 launch my_first_pkg my_launch.launch.py
```

---

## 🔧 Parameters

Parameters let you configure nodes without changing code!

### Declaring Parameters in Python

```python
class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')
        
        # Declare parameters with defaults
        self.declare_parameter('max_speed', 1.0)
        self.declare_parameter('robot_name', 'my_robot')
        self.declare_parameter('enable_debug', False)
        
        # Get parameter values
        max_speed = self.get_parameter('max_speed').value
        robot_name = self.get_parameter('robot_name').value
```

### Setting Parameters in Launch File

```python
Node(
    package='my_pkg',
    executable='my_node',
    parameters=[{
        'max_speed': 2.5,
        'robot_name': 'cleaner_bot',
        'enable_debug': True
    }]
)
```

### Setting Parameters from YAML File

**File**: `config/params.yaml`
```yaml
my_node:
  ros__parameters:
    max_speed: 1.5
    robot_name: "cleaning_robot"
    enable_debug: false
```

**Launch file:**
```python
from ament_index_python.packages import get_package_share_directory
import os

config = os.path.join(
    get_package_share_directory('my_pkg'),
    'config',
    'params.yaml'
)

Node(
    package='my_pkg',
    executable='my_node',
    parameters=[config]
)
```

---

## 🚀 Advanced Launch Features

### Topic Remapping

```python
Node(
    package='my_pkg',
    executable='my_node',
    remappings=[
        ('/old_topic', '/new_topic'),
        ('/scan', '/lidar/scan')
    ]
)
```

### Namespacing (Multiple Robots)

```python
# Robot 1
Node(
    package='my_pkg',
    executable='my_node',
    namespace='robot1'
)

# Robot 2
Node(
    package='my_pkg',
    executable='my_node',
    namespace='robot2'
)

# Creates topics: /robot1/scan and /robot2/scan
```

### Conditional Launch

```python
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration

use_sim = LaunchConfiguration('use_sim', default='true')

Node(
    package='my_pkg',
    executable='sim_node',
    condition=IfCondition(use_sim)
)
```

---

## 💻 Exercises

### Exercise 5.1: Basic Launch File
Create a launch file that starts both your publisher and subscriber.

### Exercise 5.2: Parameterized Node
Add parameters to your publisher:
- `message_prefix`: String to prefix messages with
- `publish_rate`: How often to publish (Hz)

### Exercise 5.3: Multi-Robot Simulation
Launch two instances of your publisher with different namespaces.

---

## ✅ Tests
```bash
python3 tests/test_chapter_05.py
```

---

## 🚀 Next Chapter

[Chapter 6: URDF - Robot Description](../chapter_06_urdf/README.md)

**Content expanding in next update!**
