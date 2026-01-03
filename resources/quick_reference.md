# ROS2 Quick Reference Guide

## Common Commands Cheat Sheet

### Nodes
```bash
ros2 node list                          # List running nodes
ros2 node info /node_name              # Node details
ros2 run package_name node_name        # Run a node
```

### Topics
```bash
ros2 topic list                         # List all topics
ros2 topic list -t                      # List with message types
ros2 topic echo /topic_name            # Display messages
ros2 topic info /topic_name            # Topic details
ros2 topic hz /topic_name              # Publishing frequency
ros2 topic bw /topic_name              # Bandwidth usage
ros2 topic pub /topic_name msg_type "data"  # Publish message
```

### Services
```bash
ros2 service list                       # List services
ros2 service call /service_name type args  # Call service
ros2 service type /service_name        # Service type
```

### Parameters
```bash
ros2 param list                         # List all parameters
ros2 param get /node_name param_name   # Get parameter value
ros2 param set /node_name param_name value  # Set parameter
ros2 param dump /node_name             # Save parameters to file
```

### Packages
```bash
ros2 pkg list                          # List all packages
ros2 pkg create package_name           # Create new package
ros2 pkg executables package_name      # List executables
```

### Interfaces (Messages/Services/Actions)
```bash
ros2 interface list                     # List all interfaces
ros2 interface show msg_type           # Show message structure
ros2 interface package package_name    # Interfaces in package
```

### Building
```bash
colcon build                           # Build all packages
colcon build --packages-select pkg     # Build specific package
colcon build --symlink-install         # Symlink (for Python development)
```

### Sourcing
```bash
source /opt/ros/jazzy/setup.bash       # Source ROS2
source ~/ros2_ws/install/setup.bash    # Source your workspace
```

---

## Common Message Types

### Standard Messages (std_msgs)
```python
String      # { data: "text" }
Int32       # { data: 42 }
Float64     # { data: 3.14 }
Bool        # { data: true }
```

### Geometry Messages (geometry_msgs)
```python
Point       # { x: 1.0, y: 2.0, z: 3.0 }
Vector3     # { x: 1.0, y: 2.0, z: 0.0 }
Twist       # { linear: Vector3, angular: Vector3 }
Pose        # { position: Point, orientation: Quaternion }
```

### Sensor Messages (sensor_msgs)
```python
LaserScan   # LiDAR data
Image       # Camera image
Imu         # Inertial measurement unit
PointCloud2 # 3D point cloud
```

### Navigation Messages (nav_msgs)
```python
Odometry    # Robot position & velocity
Path        # Planned path
OccupancyGrid  # Map data
```

---

## Python Node Template

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')
        
        # Publisher
        self.pub = self.create_publisher(String, 'topic', 10)
        
        # Subscriber
        self.sub = self.create_subscription(
            String, 'topic', self.callback, 10)
        
        # Timer
        self.timer = self.create_timer(1.0, self.timer_callback)
        
        # Parameters
        self.declare_parameter('my_param', 'default_value')
        
    def callback(self, msg):
        self.get_logger().info(f'Received: {msg.data}')
    
    def timer_callback(self):
        msg = String()
        msg.data = 'Hello'
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

---

## C++ Node Template

```cpp
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>

class MyNode : public rclcpp::Node {
public:
    MyNode() : Node("my_node") {
        // Publisher
        publisher_ = create_publisher<std_msgs::msg::String>("topic", 10);
        
        // Subscriber
        subscription_ = create_subscription<std_msgs::msg::String>(
            "topic", 10, 
            std::bind(&MyNode::callback, this, std::placeholders::_1));
        
        // Timer
        timer_ = create_wall_timer(
            std::chrono::seconds(1),
            std::bind(&MyNode::timer_callback, this));
    }

private:
    void callback(const std_msgs::msg::String::SharedPtr msg) {
        RCLCPP_INFO(get_logger(), "Received: %s", msg->data.c_str());
    }
    
    void timer_callback() {
        auto msg = std_msgs::msg::String();
        msg.data = "Hello";
        publisher_->publish(msg);
    }
    
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<MyNode>());
    rclcpp::shutdown();
    return 0;
}
```

---

## Launch File Template

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='my_package',
            executable='my_node',
            name='my_node_name',
            output='screen',
            parameters=[{
                'param1': 'value1',
                'param2': 42
            }],
            remappings=[
                ('old_topic', 'new_topic')
            ]
        ),
    ])
```

---

## Troubleshooting

### "Package not found"
```bash
# Did you build?
cd ~/ros2_ws && colcon build

# Did you source?
source ~/ros2_ws/install/setup.bash
```

### "No module named 'rclpy'"
```bash
# Source ROS2
source /opt/ros/jazzy/setup.bash
```

### "Permission denied" on Python script
```bash
chmod +x your_script.py
```

### Check node is publishing
```bash
ros2 topic hz /your_topic
ros2 topic echo /your_topic
```

### Debug node info
```bash
ros2 node info /your_node_name
```
