# Chapter 5: Launch Files & Parameters

**Goal**: Learn to start multiple nodes at once and configure them with parameters!

---

## 📖 What are Launch Files?

**Launch files** start multiple ROS2 nodes with one command.

**Without launch file** (tedious!):
```bash
# Terminal 1
ros2 run my_package node1

# Terminal 2
ros2 run my_package node2

# Terminal 3
ros2 run my_package node3
```

**With launch file** (easy!):
```bash
ros2 launch my_package my_launch.py
```

---

## 🎯 Basic Python Concepts Needed

### What is Python?

Python is a beginner-friendly programming language. Let's review basics:

```python
# This is a comment - Python ignores it

# Variables store data
my_number = 42
my_text = "Hello"
my_list = [1, 2, 3]

# Functions do tasks
def say_hello(name):
    print(f"Hello {name}!")
    
say_hello("Robot")  # Calls the function

# If statements make decisions
if my_number > 40:
    print("Big number!")
else:
    print("Small number")

# For loops repeat actions
for item in my_list:
    print(item)  # Prints 1, then 2, then 3
```

**Don't worry** - you'll learn by doing!

---

## 🚀 Your First Launch File

### Step 1: Create Launch Directory

```bash
cd ~/ros2_ws/src/my_robot_bringup
mkdir launch
```

---

### Step 2: Create Launch File

Create `launch/simple.launch.py`:

```python
# Import needed tools
from launch import LaunchDescription
from launch_ros.actions import Node

# This function returns the launch configuration
def generate_launch_description():
    # Create a list to hold our nodes
    return LaunchDescription([
        # Start first node
        Node(
            package='my_robot_pkg',      # Package name
            executable='talker',          # Node executable
            name='my_talker',            # Custom name
            output='screen'              # Show output in terminal
        ),
        
        # Start second node
        Node(
            package='my_robot_pkg',
            executable='listener',
            name='my_listener',
            output='screen'
        ),
    ])
```

**What each line does**:
- `from launch import...`: Gets Python tools (like importing a library)
- `def generate_launch_description():`: Creates a function (a reusable block of code)
- `return LaunchDescription([...])`: Returns a list of things to launch
- `Node(...)`: Describes one ROS2 node to start

---

### Step 3: Run Launch File

```bash
ros2 launch my_robot_bringup simple.launch.py
```

Both nodes start together! Press `Ctrl+C` to stop all nodes.

---

## 🎛️ Parameters

**Parameters** configure nodes without changing code.

### Understanding Parameters

Think of parameters like settings:
```python
# Without parameters - hard-coded
speed = 0.5  # Can't change without editing code!

# With parameters - flexible
speed = get_parameter('max_speed')  # Can change anytime!
```

---

### Creating Parameterized Node

`parameterized_talker.py`:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class ParameterizedTalker(Node):
    def __init__(self):
        super().__init__('parameterized_talker')
        
        # Declare parameters with default values
        # This says: "I accept a parameter called 'message_text'"
        self.declare_parameter('message_text', 'Hello')
        self.declare_parameter('publish_rate', 1.0)
        
        # Get parameter values
        # This reads what the user set (or uses default)
        message = self.get_parameter('message_text').value
        rate = self.get_parameter('publish_rate').value
        
        # Store them for later use
        self.message = message
        
        # Create publisher
        self.publisher = self.create_publisher(String, 'chatter', 10)
        
        # Create timer - 'rate' controls how often it runs
        self.timer = self.create_timer(1.0 / rate, self.timer_callback)
        
        self.counter = 0
        
        self.get_logger().info(f'Publishing "{message}" at {rate}Hz')
    
    def timer_callback(self):
        # This function runs repeatedly
        msg = String()
        msg.data = f'{self.message} {self.counter}'
        
        self.publisher.publish(msg)
        self.counter += 1

def main(args=None):
    rclpy.init(args=args)
    node = ParameterizedTalker()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Code Explanation** (line by line):
1. `import` - Gets tools we need
2. `class ParameterizedTalker(Node):` - Creates a new type of node
3. `def __init__(self):` - Runs when node starts
4. `self.declare_parameter(...)` - Says "I accept this parameter"
5. `self.get_parameter(...).value` - Reads the parameter value
6. `def timer_callback(self):` - Runs repeatedly (like a loop)

---

### Setting Parameters in Launch File

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='my_robot_pkg',
            executable='parameterized_talker',
            name='talker',
            parameters=[{
                'message_text': 'Robot says hi!',
                'publish_rate': 2.0
            }]
        ),
    ])
```

---

### Parameters from YAML File

**Better for many parameters!**

Create `config/robot_params.yaml`:

```yaml
# Configuration for talker node
talker:
  ros__parameters:
    message_text: "Hello from YAML!"
    publish_rate: 5.0
```

**YAML Basics**:
- Indentation matters (like Python)
- `key: value` pairs
- `#` for comments

---

Launch with YAML:

```python
import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Build path to config file
    # os.path.join combines folder paths
    config_file = os.path.join(
        get_package_share_directory('my_robot_bringup'),
        'config',
        'robot_params.yaml'
    )
    
    return LaunchDescription([
        Node(
            package='my_robot_pkg',
            executable='parameterized_talker',
            name='talker',
            parameters=[config_file]  # Load from file
        ),
    ])
```

---

## 🔄 Changing Parameters at Runtime

```bash
# List all parameters
ros2 param list

# Get parameter value
ros2 param get /talker message_text

# Set parameter value (while node is running!)
ros2 param set /talker message_text "New message!"

# Save current parameters to file
ros2 param dump /talker --output-dir ~/my_params
```

---

## 🎯 Launch File Arguments

**Let users customize launches**:

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Declare arguments (like function parameters)
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',           # Argument name
        default_value='false',    # Default if not provided
        description='Use simulation time if true'
    )
    
    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='my_robot',
        description='Name of the robot'
    )
    
    # Get argument values
    use_sim_time = LaunchConfiguration('use_sim_time')
    robot_name = LaunchConfiguration('robot_name')
    
    # Use arguments in nodes
    talker_node = Node(
        package='my_robot_pkg',
        executable='parameterized_talker',
        name='talker',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_name': robot_name
        }]
    )
    
    return LaunchDescription([
        use_sim_time_arg,
        robot_name_arg,
        talker_node,
    ])
```

**Run with arguments**:
```bash
ros2 launch my_robot_bringup talker.launch.py use_sim_time:=true robot_name:=robo1
```

---

## 📦 Including Other Launch Files

**Reuse existing launch files**:

```python
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Get path to another launch file
    gazebo_launch = os.path.join(
        get_package_share_directory('gazebo_ros'),
        'launch',
        'gazebo.launch.py'
    )
    
    return LaunchDescription([
        # Include Gazebo launch
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gazebo_launch),
            launch_arguments={'verbose': 'true'}.items()
        ),
        
        # Add our own nodes
        Node(
            package='my_robot_pkg',
            executable='controller',
            name='robot_controller'
        ),
    ])
```

---

## 🌐 Namespacing (Multiple Robots)

**Run same nodes for different robots**:

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Robot 1
        Node(
            package='my_robot_pkg',
            executable='controller',
            name='controller',
            namespace='robot1',  # All topics prefixed with /robot1/
        ),
        
        # Robot 2
        Node(
            package='my_robot_pkg',
            executable='controller',
            name='controller',
            namespace='robot2',  # All topics prefixed with /robot2/
        ),
    ])
```

Now you have:
- `/robot1/cmd_vel`
- `/robot2/cmd_vel`

---

## 💻 Complete Example: Robot Bringup

`launch/robot_bringup.launch.py`:

```python
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Get package directory
    pkg_dir = get_package_share_directory('my_robot_bringup')
    
    # Config file path
    config_file = os.path.join(pkg_dir, 'config', 'robot_params.yaml')
    
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time')
    
    return LaunchDescription([
        # Argument
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation time'
        ),
        
        # Robot state publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'use_sim_time': use_sim_time}]
        ),
        
        # Sensor node
        Node(
            package='my_robot_sensors',
            executable='lidar_reader',
            name='lidar_reader',
            parameters=[config_file, {'use_sim_time': use_sim_time}]
        ),
        
        # Controller node
        Node(
            package='my_robot_control',
            executable='controller',
            name='controller',
            parameters=[config_file, {'use_sim_time': use_sim_time}],
            output='screen'
        ),
    ])
```

---

## 🐛 Debugging Launch Files

### Check syntax
```bash
# Python syntax check
python3 launch/my_launch.py
```

### Common errors

**Error: "No module named 'launch'"**
```bash
# Install launch packages
sudo apt install ros-jazzy-launch ros-jazzy-launch-ros
```

**Error: "Package not found"**
```bash
# Rebuild workspace
cd ~/ros2_ws
colcon build
source install/setup.bash
```

**Error: "File not found"**
- Check paths in `os.path.join()`
- Use `get_package_share_directory()` for portability

---

## 💻 Exercises

### Exercise 5.1: Multi-Node Launch

Create a launch file that starts:
1. Publisher node
2. Subscriber node
3. Both with custom names

### Exercise 5.2: Parameterized Nodes

Create a node with parameters:
- `robot_name` (string)
- `max_speed` (float)
- `enabled` (bool)

Load parameters from YAML file.

### Exercise 5.3: Conditional Launch

Create a launch file with argument `enable_camera`. Only start camera node if `true`.

**Hint**:
```python
from launch.conditions import IfCondition

Node(
    ...,
    condition=IfCondition(LaunchConfiguration('enable_camera'))
)
```

---

## 🎯 Key Takeaways

1. **Launch files** start multiple nodes with one command
2. **Parameters** configure nodes without code changes
3. **YAML files** store parameter values
4. **Arguments** let users customize launches
5. **Namespacing** runs multiple robots
6. **Include** reuses existing launch files

---

## 🚀 Next Chapter

[Chapter 6: URDF Robot Description](../chapter_06_urdf/README.md) - Define your robot's physical structure!

---

## 📚 Resources

- [Launch System](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Launch/Launch-Main.html)
- [Parameters](https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Parameters/Understanding-ROS2-Parameters.html)
- [YAML Syntax](https://yaml.org/spec/1.2.2/)
