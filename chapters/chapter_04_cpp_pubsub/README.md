# Chapter 4: C++ Publishers & Subscribers

**Goal**: Learn C++ in ROS2, understand when to use C++ vs Python, and compare performance.

---

## 📖 Why C++?

### When to Use C++
- **High-frequency operations** (>100 Hz): Camera processing, LiDAR filtering
- **Low latency requirements**: Real-time control loops
- **Resource constraints**: Embedded systems
- **Performance critical**: Path planning algorithms
- **Production deployment**: Industrial robots

### When to Use Python
- **Rapid prototyping**: Quick testing
- **High-level logic**: Behavior coordination
- **Data processing**: Machine learning pipelines
- **Less than 100 Hz**: Most sensor processing
- **Learning**: Easier to understand

---

## 🏗️ Creating a C++ Package

```bash
cd ~/ros2_ws/src

# Create C++ package
ros2 pkg create --build-type ament_cmake my_cpp_pkg \
  --dependencies rclcpp std_msgs
```

**Package structure:**
```
my_cpp_pkg/
├── CMakeLists.txt       # Build configuration
├── package.xml          # Package metadata
├── include/             # Header files (.hpp)
│   └── my_cpp_pkg/
└── src/                 # Source files (.cpp)
    ├── simple_publisher.cpp
    └── simple_subscriber.cpp
```

---

## 📝 C++ Publisher Node

**File**: `~/ros2_ws/src/my_cpp_pkg/src/simple_publisher.cpp`

```cpp
#include <chrono>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using namespace std::chrono_literals;

/**
 * Simple Publisher Node in C++
 * Publishes "Hello World" messages to /chatter topic
 */
class SimplePublisher : public rclcpp::Node
{
public:
    SimplePublisher() : Node("simple_publisher"), counter_(0)
    {
        // Create publisher
        publisher_ = this->create_publisher<std_msgs::msg::String>("chatter", 10);
        
        // Create timer (500ms)
        timer_ = this->create_wall_timer(
            500ms,
            std::bind(&SimplePublisher::timer_callback, this));
        
        RCLCPP_INFO(this->get_logger(), "Simple Publisher has started!");
    }

private:
    void timer_callback()
    {
        auto message = std_msgs::msg::String();
        message.data = "Hello World: " + std::to_string(counter_);
        
        RCLCPP_INFO(this->get_logger(), "Publishing: '%s'", message.data.c_str());
        publisher_->publish(message);
        
        counter_++;
    }
    
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
    size_t counter_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<SimplePublisher>());
    rclcpp::shutdown();
    return 0;
}
```

---

## 👂 C++ Subscriber Node

**File**: `~/ros2_ws/src/my_cpp_pkg/src/simple_subscriber.cpp`

```cpp
#include <memory>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

/**
 * Simple Subscriber Node in C++
 * Listens to /chatter topic
 */
class SimpleSubscriber : public rclcpp::Node
{
public:
    SimpleSubscriber() : Node("simple_subscriber")
    {
        // Create subscriber
        subscription_ = this->create_subscription<std_msgs::msg::String>(
            "chatter",
            10,
            std::bind(&SimpleSubscriber::topic_callback, this, std::placeholders::_1));
        
        RCLCPP_INFO(this->get_logger(), "Simple Subscriber has started!");
    }

private:
    void topic_callback(const std_msgs::msg::String::SharedPtr msg)
    {
        RCLCPP_INFO(this->get_logger(), "I heard: '%s'", msg->data.c_str());
    }
    
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<SimpleSubscriber>());
    rclcpp::shutdown();
    return 0;
}
```

---

## ⚙️ CMakeLists.txt Configuration

**Edit**: `~/ros2_ws/src/my_cpp_pkg/CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.8)
project(my_cpp_pkg)

# Compiler options
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

# Build publisher
add_executable(simple_publisher src/simple_publisher.cpp)
ament_target_dependencies(simple_publisher rclcpp std_msgs)

# Build subscriber
add_executable(simple_subscriber src/simple_subscriber.cpp)
ament_target_dependencies(simple_subscriber rclcpp std_msgs)

# Install executables
install(TARGETS
  simple_publisher
  simple_subscriber
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
```

---

## 🔨 Build and Run

```bash
# Build
cd ~/ros2_ws
colcon build --packages-select my_cpp_pkg

# Source
source install/setup.bash

# Run publisher
ros2 run my_cpp_pkg simple_publisher

# Run subscriber (in another terminal)
ros2 run my_cpp_pkg simple_subscriber
```

---

## 🔍 Python vs C++ Comparison

| Aspect | Python | C++ |
|--------|--------|-----|
| **Speed** | ~0.5-2ms latency | ~0.01-0.1ms latency |
| **Memory** | Higher | Lower |
| **Code Lines** | Fewer | More |
| **Learning Curve** | Easy | Moderate |
| **Compile Time** | No compilation | Must compile |
| **Best For** | High-level logic | Performance-critical |

**Rule of Thumb**: Start with Python, move to C++ only when you need performance!

---

## 💻 Exercises

### Exercise 4.1: Port to C++
Convert your Exercise 3.4 (number publisher/subscriber) to C++ using `Int32` messages.

### Exercise 4.2: Performance Test
Create a publisher that publishes at 100 Hz in both Python and C++. Use `ros2 topic hz` to verify actual rate.

### Exercise 4.3: Mixed Language
Run Python publisher with C++ subscriber. Verify they communicate perfectly!

---

## ✅ Tests

```bash
cd ~/rostutorial/chapters/chapter_04_cpp_pubsub
python3 tests/test_chapter_04.py
```

---

## 🚀 Next Chapter

[Chapter 5: Launch Files & Parameters](../chapter_05_launch_params/README.md) - Learn to start multiple nodes and configure them!

---

## 📚 C++ Quick Reference

### Key Differences from Python

```cpp
// Include headers
#include <rclcpp/rclcpp.hpp>

// Class inheritance
class MyNode : public rclcpp::Node

// Constructor
MyNode() : Node("node_name")

// Publisher
auto pub = create_publisher<MsgType>("topic", 10);
pub->publish(msg);

// Subscriber
auto sub = create_subscription<MsgType>(
    "topic", 10, callback);

// Timer
auto timer = create_wall_timer(duration, callback);

// Logging
RCLCPP_INFO(get_logger(), "Message");

// Main
rclcpp::init(argc, argv);
rclcpp::spin(node);
rclcpp::shutdown();
```

---

## 🔍 Side-by-Side Comparison

Let's compare the same functionality in Python vs C++:

### Creating a Publisher

**Python:**
```python
self.publisher_ = self.create_publisher(String, 'chatter', 10)
```

**C++:**
```cpp
publisher_ = this->create_publisher<std_msgs::msg::String>("chatter", 10);
```

### Timer Callback

**Python:**
```python
self.timer = self.create_timer(0.5, self.timer_callback)
```

**C++:**
```cpp
timer_ = this->create_wall_timer(
    500ms,  // or std::chrono::milliseconds(500)
    std::bind(&SimplePublisher::timer_callback, this));
```

### Logging

**Python:**
```python
self.get_logger().info(f'Publishing: "{msg.data}"')
```

**C++:**
```cpp
RCLCPP_INFO(this->get_logger(), "Publishing: '%s'", msg.data.c_str());
```

---

## 💻 Complete Exercises

### Exercise 4.1: Create the C++ Package

**Step 1**: Create package
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake my_cpp_pkg \
  --dependencies rclcpp std_msgs
```

**Step 2**: Copy the source files from `examples/` to your package:
```bash
# Copy publisher
cp ~/rostutorial/chapters/chapter_04_cpp_pubsub/examples/simple_publisher.cpp \
   ~/ros2_ws/src/my_cpp_pkg/src/

# Copy subscriber  
cp ~/rostutorial/chapters/chapter_04_cpp_pubsub/examples/simple_subscriber.cpp \
   ~/ros2_ws/src/my_cpp_pkg/src/
```

**Step 3**: Update CMakeLists.txt (copy from examples folder or edit manually)

**Step 4**: Build
```bash
cd ~/ros2_ws
colcon build --packages-select my_cpp_pkg
source install/setup.bash
```

**Step 5**: Run
```bash
# Terminal 1
ros2 run my_cpp_pkg simple_publisher

# Terminal 2
ros2 run my_cpp_pkg simple_subscriber
```

---

### Exercise 4.2: Create Int32 Publisher in C++

Create a C++ node that publishes integers (similar to Python Exercise 3.4).

**Hints:**
```cpp
#include "std_msgs/msg/int32.hpp"

// In class
rclcpp::Publisher<std_msgs::msg::Int32>::SharedPtr publisher_;

// In timer callback
auto msg = std_msgs::msg::Int32();
msg.data = counter_;
publisher_->publish(msg);
```

**File**: `~/ros2_ws/src/my_cpp_pkg/src/number_publisher.cpp`

Don't forget to add it to CMakeLists.txt!

---

### Exercise 4.3: Performance Comparison

Compare Python vs C++ publishing rates:

```bash
# Test Python publisher frequency
ros2 run my_first_pkg simple_publisher &
ros2 topic hz /chatter

# Test C++ publisher frequency  
ros2 run my_cpp_pkg simple_publisher &
ros2 topic hz /chatter
```

**Expected**: Both should publish at ~2 Hz (every 0.5s). For this simple example, performance is similar!

---

### Exercise 4.4: High-Frequency Publisher

Modify the C++ publisher to publish at 100 Hz (every 10ms):

```cpp
// Change timer period
timer_ = this->create_wall_timer(
    10ms,  // 10 milliseconds = 100 Hz
    std::bind(&SimplePublisher::timer_callback, this));
```

Try the same with Python and compare CPU usage!

---

## 🐛 Common C++ Issues

### "undefined reference to `std::__cxx11::basic_string"
- **Fix**: Make sure you're using C++14 or higher
- Add to CMakeLists.txt: `set(CMAKE_CXX_STANDARD 14)`

### "ament_target_dependencies: command not found"
- **Fix**: You're using ament_cmake, not ament_python
- Check your package was created with `--build-type ament_cmake`

### "No executable found"
- **Fix**: Add executable to CMakeLists.txt install section
- Rebuild: `colcon build --packages-select my_cpp_pkg`

### "error: 'msg' was not declared in this scope"
- **Fix**: Use `auto msg = std_msgs::msg::String();`
- Or declare type: `std_msgs::msg::String msg;`

---

## 📊 When to Actually Use C++

Based on real-world ROS2 development:

### ✅ Use C++ for:
1. **High-frequency control loops** (>100 Hz)
   - Motor control
   - Real-time sensor processing
2. **Performance-critical paths**
   - SLAM algorithms
   - Path planning
   - Image processing
3. **Low-latency requirements**
   - Safety systems
   - Emergency stops
4. **Libraries and reusable components**
   - When you need maximum compatibility

### ✅ Use Python for:
1. **Rapid prototyping**
2. **High-level logic**
   - State machines
   - Behavior trees
3. **Integration with ML/AI**
   - TensorFlow, PyTorch
4. **Data analysis and visualization**
5. **Most application-level code**

### 💡 Best Practice
**Start with Python, profile your system, convert to C++ only where needed!**

Most robots use **both**:
- C++ for low-level control and performance
- Python for high-level logic and behaviors

---

## 🎓 Key Takeaways

1. **C++ is faster** but requires more code
2. **Python is easier** but slightly slower
3. **Same ROS2 API** - concepts translate directly
4. **CMake** builds C++ packages
5. **Templates** (`<Type>`) are everywhere in C++
6. **Smart pointers** (`SharedPtr`) manage memory
7. **Both languages** can talk to each other seamlessly!

---
