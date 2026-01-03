# Chapter 2: ROS2 Core Concepts

**Goal**: Understand the fundamental architecture of ROS2 and how components communicate.

---

## 📖 The ROS2 Communication Model

ROS2 uses a **publish-subscribe** pattern and **client-server** pattern for communication. Let's understand each:

### 1. Topics (Publish-Subscribe) 📡

**Use case**: Continuous data streams (sensor data, robot state, etc.)

```
┌─────────────┐                          ┌──────────────┐
│  Publisher  │──── Topic: /scan ────────│  Subscriber  │
│  (LiDAR)    │                          │  (SLAM Node) │
└─────────────┘                          └──────────────┘
                                                 │
                                         ┌──────────────┐
                                         │  Subscriber  │
                                         │  (Nav Node)  │
                                         └──────────────┘
```

**Characteristics:**
- **One-to-many**: One publisher, multiple subscribers
- **Asynchronous**: Publisher doesn't wait for subscribers
- **No reply**: Fire and forget
- **Continuous**: Data flows constantly

**Example**: LiDAR publishes scan data. SLAM node subscribes to create maps. Navigation node also subscribes to avoid obstacles.

---

### 2. Services (Request-Response) 🔄

**Use case**: Occasional operations that need a response (save map, reset odometry, etc.)

```
┌─────────────┐                          ┌──────────────┐
│   Client    │──── Service Request ────▶│    Server    │
│             │                          │              │
│             │◀─── Service Response ────│              │
└─────────────┘                          └──────────────┘
```

**Characteristics:**
- **Synchronous**: Client waits for response
- **Request-reply**: Two-way communication
- **Occasional**: Not meant for continuous data

**Example**: A "save_map" service. You call it, it saves the map, returns success/failure.

---

### 3. Actions (Long-Running Tasks) ⏱️

**Use case**: Tasks that take time and need progress updates (navigate to goal, pick object, etc.)

```
┌─────────────┐                          ┌──────────────┐
│   Client    │──── Goal ────────────────▶│    Server    │
│             │◀─── Feedback ────────────│              │
│             │◀─── Feedback ────────────│              │
│             │◀─── Feedback ────────────│              │
│             │◀─── Result ──────────────│              │
└─────────────┘                          └──────────────┘
```

**Characteristics:**
- **Goal-oriented**: Send a goal, get updates
- **Feedback**: Regular progress updates
- **Cancelable**: Can abort mid-execution
- **Result**: Final outcome when done

**Example**: "Navigate to point (5, 10)". You get feedback on progress, can cancel, and get final success/failure.

---

## 🧱 ROS2 Architecture Components

### Nodes
- **Independent processes** that perform computation
- Should do **one specific task** well
- Communicate via topics/services/actions
- Written in Python or C++

**Example nodes in a robot:**
- `lidar_driver` - Reads LiDAR hardware
- `slam_node` - Creates maps
- `motor_controller` - Controls motors
- `navigation_node` - Plans paths

### Packages
- **Organizational units** containing nodes, launch files, configs
- Like a library or module
- Can depend on other packages

**Structure:**
```
my_robot_pkg/
├── CMakeLists.txt or setup.py
├── package.xml
├── launch/
├── config/
├── src/  (for C++)
└── my_robot_pkg/  (for Python)
```

### Launch Files
- **Start multiple nodes** at once with configuration
- Python files (.py) in ROS2
- Can set parameters, remap topics, etc.

### Parameters
- **Configuration values** for nodes
- Can change behavior without recompiling
- Example: `max_speed`, `sensor_frame_id`, `update_rate`

---

## 🔍 Understanding Message Types

Messages are **data structures** sent over topics. ROS2 provides standard ones and you can create custom ones.

### Common Message Types

#### 1. **String** (`std_msgs/msg/String`)
```python
data: "Hello World"
```

#### 2. **LaserScan** (`sensor_msgs/msg/LaserScan`)
```python
angle_min: -3.14
angle_max: 3.14
ranges: [1.5, 1.6, 1.7, ...]  # distances in meters
intensities: [...]
```

#### 3. **Twist** (`geometry_msgs/msg/Twist`)
Used for velocity commands:
```python
linear:
  x: 0.5  # forward/backward (m/s)
  y: 0.0  # left/right (for mecanum)
  z: 0.0  # up/down (for drones)
angular:
  x: 0.0  # roll
  y: 0.0  # pitch
  z: 0.3  # yaw (rotation)
```

#### 4. **Odometry** (`nav_msgs/msg/Odometry`)
Robot position and velocity:
```python
pose:
  position: {x: 1.0, y: 2.0, z: 0.0}
  orientation: {x: 0, y: 0, z: 0, w: 1}
twist:
  linear: {x: 0.5, y: 0, z: 0}
  angular: {x: 0, y: 0, z: 0.1}
```

---

## 💻 Hands-On: Exploring ROS2

### Exercise 2.1: Inspect the Demo

Start the talker and listener from Chapter 1 again:

```bash
# Terminal 1
ros2 run demo_nodes_cpp talker

# Terminal 2
ros2 run demo_nodes_py listener
```

Now in **Terminal 3**, run these commands and observe:

```bash
# 1. View computational graph
ros2 node list
# Shows: /talker, /listener

# 2. Get info about a node
ros2 node info /talker

# 3. View all topics
ros2 topic list

# 4. Get topic details
ros2 topic info /chatter
# Shows: Type, Publisher count, Subscriber count

# 5. View message structure
ros2 interface show std_msgs/msg/String

# 6. Echo messages (see them in real-time)
ros2 topic echo /chatter

# 7. Check publishing frequency
ros2 topic hz /chatter

# 8. Publish manually
ros2 topic pub /chatter std_msgs/msg/String "data: 'Hello from command line'"
```

**What you learned:**
- How to inspect running nodes
- How to see topic information
- How to interact with topics from command line

---

### Exercise 2.2: Understanding Message Flow

Let's create a more complex scenario. We'll have multiple subscribers to one topic.

**Terminal 1** - Publisher:
```bash
ros2 run demo_nodes_cpp talker
```

**Terminal 2** - Subscriber 1:
```bash
ros2 run demo_nodes_py listener
```

**Terminal 3** - Subscriber 2:
```bash
ros2 run demo_nodes_cpp listener
```

**Terminal 4** - Inspect:
```bash
ros2 topic info /chatter
# Notice: 1 publisher, 2 subscribers!

ros2 node list
# Shows: /talker, /listener (multiple instances)
```

**Observation**: One publisher can send to multiple subscribers simultaneously. This is the power of the publish-subscribe pattern!

---

### Exercise 2.3: Turtle Simulator (Services & Actions)

Let's explore services and actions using the turtle simulator:

```bash
# Start the simulator
ros2 run turtlesim turtlesim_node
```

You should see a blue window with a turtle. Now explore:

**Topics** (continuous data):
```bash
# List all topics
ros2 topic list
# /turtle1/cmd_vel - controls the turtle
# /turtle1/pose - turtle's position

# See the turtle's position
ros2 topic echo /turtle1/pose

# Move the turtle (publish to cmd_vel)
ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}"
```

**Services** (request-response):
```bash
# List services
ros2 service list
# /clear, /spawn, /kill, /reset, etc.

# Call the clear service (erases turtle's trail)
ros2 service call /clear std_srvs/srv/Empty

# Spawn a new turtle
ros2 service call /spawn turtlesim/srv/Spawn \
  "{x: 5.0, y: 5.0, theta: 0.0, name: 'turtle2'}"
```

**Control with keyboard**:
```bash
ros2 run turtlesim turtle_teleop_key
# Use arrow keys to move the turtle
```

---

## 🎯 Key Concepts Summary

| Concept | Purpose | Example |
|---------|---------|---------|
| **Node** | Independent program | `lidar_driver`, `slam_node` |
| **Topic** | Continuous data stream | `/scan`, `/cmd_vel` |
| **Message** | Data structure | `LaserScan`, `Twist` |
| **Service** | Request-response | `save_map`, `reset_odometry` |
| **Action** | Long task with feedback | `navigate_to_pose` |
| **Package** | Code organization | `my_robot_bringup` |
| **Launch File** | Start multiple nodes | `robot.launch.py` |
| **Parameter** | Configuration value | `max_velocity: 1.5` |

---

## 🧪 Practical Exercise: Create Mental Model

Draw a diagram of this scenario (on paper or digitally):

**Cleaning Robot System:**
1. LiDAR sensor publishes to `/scan` topic
2. SLAM node subscribes to `/scan`, publishes to `/map`
3. Navigation node subscribes to `/scan` and `/map`, publishes to `/cmd_vel`
4. Motor controller subscribes to `/cmd_vel`
5. A service `/save_map` saves the current map
6. An action `/navigate_to_pose` moves the robot to a goal

**Questions:**
- Which communication pattern (topic/service/action) is used for each?
- Why is `/scan` a topic and not a service?
- Why is navigation an action and not a topic?

---

## ✅ Tests

Run the test to verify your understanding:

```bash
cd ~/rostutorial/chapters/chapter_02_core_concepts
python3 tests/test_chapter_02.py
```

This test will:
- Quiz you on concepts
- Test your ability to inspect nodes and topics
- Verify you understand message types

---

## 🎯 Key Takeaways

1. **Topics** are for continuous data (sensor readings)
2. **Services** are for occasional requests (save, reset)
3. **Actions** are for long tasks with feedback (navigation)
4. **Nodes** should be small and focused (one job)
5. **Messages** define data structure
6. ROS2 command line tools let you inspect everything

---

## 🚀 Next Chapter

Ready for actual coding? In [Chapter 3](../chapter_03_python_pubsub/README.md), you'll create your first Python publisher and subscriber nodes from scratch!

---

## 📚 Cheat Sheet

```bash
# Nodes
ros2 node list                           # List all nodes
ros2 node info <node_name>              # Node details

# Topics
ros2 topic list                          # List all topics
ros2 topic info <topic_name>            # Topic details
ros2 topic echo <topic_name>            # See messages
ros2 topic hz <topic_name>              # Publishing rate
ros2 topic pub <topic> <type> <data>    # Publish manually

# Services
ros2 service list                        # List services
ros2 service call <service> <type> <data>  # Call service

# Messages/Interfaces
ros2 interface list                      # All message types
ros2 interface show <type>              # Message structure

# General
ros2 --help                             # All commands
```
