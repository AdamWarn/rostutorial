# Chapter 10: Custom Messages & Interfaces

**Goal**: Learn to create your own ROS2 message types for robot-specific data!

---

## 📖 Why Custom Messages?

Built-in messages (`std_msgs`, `geometry_msgs`, `sensor_msgs`) are great, but sometimes you need custom data:

```python
# ❌ Using multiple topics - messy!
pub_battery = publisher(Float32, '/battery')
pub_cleaning = publisher(Bool, '/is_cleaning')
pub_coverage = publisher(Float32, '/coverage_percent')

# ✅ Custom message - organized!
pub_status = publisher(RobotStatus, '/robot_status')
```

**Custom messages let you**:
- Group related data
- Enforce data structure
- Make code cleaner
- Create robot-specific APIs

---

## 📦 Message Types in ROS2

### Message Files (.msg)

Define data structures:

```
# BatteryStatus.msg
float32 voltage
float32 current
float32 percentage
string status  # "charging", "discharging", "full"
```

### Service Files (.srv)

Define request-response interfaces:

```
# SetSpeed.srv
float32 max_speed
---
bool success
string message
```

### Action Files (.action)

Define long-running tasks with feedback:

```
# CleanArea.action
# Goal
float32 area_size
---
# Result
float32 coverage_achieved
---
# Feedback
float32 current_coverage
```

---

## 🛠️ Creating a Custom Message Package

### Step 1: Create Package

```bash
cd ~/ros2_ws/src
ros2 pkg create my_robot_interfaces \
  --build-type ament_cmake \
  --dependencies std_msgs geometry_msgs

cd my_robot_interfaces
```

**Important**: Use `ament_cmake`, not `ament_python`! Message packages must use CMake.

---

### Step 2: Create Message Directory

```bash
mkdir msg
```

---

### Step 3: Create Message File

Create `msg/RobotStatus.msg`:

```
# RobotStatus.msg - Overall robot state

# Battery information
float32 battery_voltage
float32 battery_percentage

# Cleaning state
bool is_cleaning
float32 coverage_percentage

# Position (odometry)
float32 x
float32 y
float32 yaw

# Status
string mode  # "idle", "cleaning", "charging", "error"
string error_message
```

---

### Step 4: Update package.xml

Add these lines to `package.xml`:

```xml
<buildtool_depend>rosidl_default_generators</buildtool_depend>
<exec_depend>rosidl_default_runtime</exec_depend>
<member_of_group>rosidl_interface_packages</member_of_group>
```

---

### Step 5: Update CMakeLists.txt

Add to `CMakeLists.txt`:

```cmake
find_package(rosidl_default_generators REQUIRED)

# Declare messages
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/RobotStatus.msg"
  DEPENDENCIES std_msgs geometry_msgs
)
```

---

### Step 6: Build

```bash
cd ~/ros2_ws
colcon build --packages-select my_robot_interfaces
source install/setup.bash
```

---

### Step 7: Verify

```bash
# List all interfaces in package
ros2 interface list | grep my_robot_interfaces

# Show message definition
ros2 interface show my_robot_interfaces/msg/RobotStatus
```

---

## 💻 Using Custom Messages

### In Python

```python
from my_robot_interfaces.msg import RobotStatus

class StatusPublisher(Node):
    def __init__(self):
        super().__init__('status_publisher')
        
        self.publisher = self.create_publisher(
            RobotStatus,
            '/robot_status',
            10)
        
        self.timer = self.create_timer(1.0, self.publish_status)
    
    def publish_status(self):
        msg = RobotStatus()
        msg.battery_voltage = 12.5
        msg.battery_percentage = 85.0
        msg.is_cleaning = True
        msg.coverage_percentage = 42.5
        msg.x = 3.2
        msg.y = 1.5
        msg.yaw = 0.78
        msg.mode = "cleaning"
        msg.error_message = ""
        
        self.publisher.publish(msg)
        self.get_logger().info(f'Status: {msg.mode} @ {msg.coverage_percentage}%')
```

### Subscriber

```python
class StatusSubscriber(Node):
    def __init__(self):
        super().__init__('status_subscriber')
        
        self.subscription = self.create_subscription(
            RobotStatus,
            '/robot_status',
            self.status_callback,
            10)
    
    def status_callback(self, msg):
        self.get_logger().info(
            f'Battery: {msg.battery_percentage:.1f}% | '
            f'Mode: {msg.mode} | '
            f'Coverage: {msg.coverage_percentage:.1f}%')
```

---

## 🔧 Adding Dependencies

If your package uses custom messages, update its `package.xml`:

```xml
<depend>my_robot_interfaces</depend>
```

And `CMakeLists.txt` (for ament_cmake):

```cmake
find_package(my_robot_interfaces REQUIRED)

rosidl_target_interfaces(my_node
  ${PROJECT_NAME} "rosidl_typesupport_cpp")
```

Or in Python packages, just import normally!

---

## 📝 More Message Examples

### Obstacle Message

```
# Obstacle.msg
float32 distance
float32 angle
string type  # "wall", "furniture", "stairs", etc.
```

### CleaningCommand

```
# CleaningCommand.msg
string command  # "start", "stop", "pause", "resume", "dock"
float32[] target_area  # [x_min, x_max, y_min, y_max]
```

### Waypoint

```
# Waypoint.msg
float32 x
float32 y
float32 yaw
string action  # "move", "clean", "wait"
float32 duration
```

---

## 🎯 Creating a Service

### Step 1: Create Service Directory

```bash
cd my_robot_interfaces
mkdir srv
```

### Step 2: Create Service File

Create `srv/SetCleaningMode.srv`:

```
# Request
string mode  # "normal", "turbo", "quiet"
---
# Response
bool success
string message
```

---

### Step 3: Update CMakeLists.txt

```cmake
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/RobotStatus.msg"
  "srv/SetCleaningMode.srv"  # Add this
  DEPENDENCIES std_msgs
)
```

---

### Step 4: Build and Use

```bash
colcon build --packages-select my_robot_interfaces
source install/setup.bash

# Verify
ros2 interface show my_robot_interfaces/srv/SetCleaningMode
```

**Service server**:

```python
from my_robot_interfaces.srv import SetCleaningMode

class CleaningService(Node):
    def __init__(self):
        super().__init__('cleaning_service')
        
        self.srv = self.create_service(
            SetCleaningMode,
            '/set_cleaning_mode',
            self.handle_mode_change)
        
        self.current_mode = "normal"
    
    def handle_mode_change(self, request, response):
        valid_modes = ["normal", "turbo", "quiet"]
        
        if request.mode in valid_modes:
            self.current_mode = request.mode
            response.success = True
            response.message = f"Mode set to {request.mode}"
        else:
            response.success = False
            response.message = f"Invalid mode: {request.mode}"
        
        return response
```

**Service client**:

```python
class ModeChanger(Node):
    def __init__(self):
        super().__init__('mode_changer')
        
        self.client = self.create_client(
            SetCleaningMode,
            '/set_cleaning_mode')
    
    def change_mode(self, new_mode):
        request = SetCleaningMode.Request()
        request.mode = new_mode
        
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        
        if future.result().success:
            self.get_logger().info(future.result().message)
```

---

## 🎬 Creating an Action

### Step 1: Create Action File

```bash
mkdir action
```

Create `action/Navigate.action`:

```
# Goal
float32 target_x
float32 target_y
float32 target_yaw
---
# Result
bool success
float32 final_distance_error
float32 time_elapsed
---
# Feedback
float32 distance_remaining
float32 estimated_time_remaining
```

---

### Step 2: Update CMakeLists.txt

```cmake
find_package(action_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/RobotStatus.msg"
  "srv/SetCleaningMode.srv"
  "action/Navigate.action"  # Add this
  DEPENDENCIES std_msgs action_msgs
)
```

---

### Step 3: Update package.xml

```xml
<depend>action_msgs</depend>
```

---

### Step 4: Build

```bash
colcon build --packages-select my_robot_interfaces
source install/setup.bash

ros2 interface show my_robot_interfaces/action/Navigate
```

---

## 💻 Exercises

### Exercise 10.1: Create BatteryStatus Message

Create a custom message for battery information:

```
# BatteryStatus.msg
float32 voltage
float32 current
float32 temperature
uint8 percentage  # 0-100
bool is_charging
```

Build and test it!

---

### Exercise 10.2: Create ResetOdometry Service

Create a service to reset robot's odometry:

```
# ResetOdometry.srv
float32 new_x
float32 new_y
float32 new_yaw
---
bool success
string message
```

---

### Exercise 10.3: Nested Messages

Create a message that uses another message:

```
# FullRobotState.msg
RobotStatus status  # Your previous message!
BatteryStatus battery
geometry_msgs/Twist current_velocity
```

---

## 📂 Complete Package Structure

```
my_robot_interfaces/
├── CMakeLists.txt
├── package.xml
├── msg/
│   ├── RobotStatus.msg
│   ├── BatteryStatus.msg
│   └── Obstacle.msg
├── srv/
│   ├── SetCleaningMode.srv
│   └── ResetOdometry.srv
└── action/
    └── Navigate.action
```

---

## 🐛 Common Issues

### Build fails with "rosidl_generate_interfaces"
- Make sure `rosidl_default_generators` in `package.xml`
- Use `ament_cmake`, not `ament_python`

### Import fails in Python
- Did you source install? `source ~/ros2_ws/install/setup.bash`
- Check package built: `ros2 pkg list | grep my_robot_interfaces`

### "No module named 'my_robot_interfaces'"
- Build interface package first
- Source workspace
- Rebuild dependent packages

---

## 🎯 Key Takeaways

1. **Custom messages** organize robot-specific data
2. **Interface packages** use `ament_cmake`, not Python
3. **Three types**: Messages (.msg), Services (.srv), Actions (.action)
4. **Build with** `rosidl_generate_interfaces`
5. **Always source** after building: `source install/setup.bash`

---

## 🚀 Next Steps

Now that you know fundamentals, it's time to build your SLAM system!

**Next**: [Chapter 11: Launch Files (Advanced)](../chapter_11_launch_advanced/README.md)

Or jump to SLAM: [Chapter 12: Implementing SLAM](../chapter_12_slam/README.md)

---

## 📚 Resources

- [Creating Custom Messages](https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.html)
- [rosidl Documentation](https://docs.ros.org/en/jazzy/Concepts/About-ROS-Interfaces.html)
- [Action Tutorials](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Writing-an-Action-Server-Client/Cpp.html)
