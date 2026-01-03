# Chapter 3: Python Publishers & Subscribers

**Goal**: Create your first ROS2 nodes in Python - a publisher and subscriber that communicate via topics.

---

## 📖 Understanding Publishers & Subscribers

In this chapter, you'll build the fundamental building blocks of ROS2 communication:

- **Publisher**: Sends messages to a topic
- **Subscriber**: Receives messages from a topic

**Real-world analogy**: Think of a radio station (publisher) broadcasting on FM 101.5 (topic). Many people (subscribers) can tune in to listen.

---

## 🏗️ Creating Your First ROS2 Package

### Step 1: Create a Package

```bash
# Navigate to your workspace
cd ~/ros2_ws/src

# Create a Python package
ros2 pkg create --build-type ament_python my_first_pkg \
  --dependencies rclpy std_msgs

# What this does:
# - Creates a Python package named "my_first_pkg"
# - Adds dependency on rclpy (ROS2 Python library)
# - Adds dependency on std_msgs (standard messages)
```

Your package structure:
```
my_first_pkg/
├── package.xml          # Package metadata & dependencies
├── setup.py             # Python package setup
├── setup.cfg            # Configuration
├── resource/
├── test/
└── my_first_pkg/        # Your Python code goes here
    └── __init__.py
```

---

## 📝 Publisher Node: Talking to the World

### The Code

Create `~/ros2_ws/src/my_first_pkg/my_first_pkg/simple_publisher.py`:

```python
#!/usr/bin/env python3
"""
Simple Publisher Node
Publishes "Hello World" messages to /chatter topic
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimplePublisher(Node):
    """
    A simple publisher node that sends messages periodically.
    
    This demonstrates:
    - Creating a ROS2 node class
    - Creating a publisher
    - Using a timer for periodic execution
    """
    
    def __init__(self):
        # Initialize the node with a name
        super().__init__('simple_publisher')
        
        # Create a publisher
        # - Message type: String
        # - Topic name: 'chatter' (becomes '/chatter' with leading /)
        # - Queue size: 10 (how many messages to buffer)
        self.publisher_ = self.create_publisher(String, 'chatter', 10)
        
        # Create a timer that calls our callback every 0.5 seconds
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        # Counter for our messages
        self.counter = 0
        
        # Log that we've started
        self.get_logger().info('Simple Publisher has started!')
    
    def timer_callback(self):
        """
        This function is called every 0.5 seconds by the timer.
        It creates and publishes a message.
        """
        # Create a message
        msg = String()
        msg.data = f'Hello World: {self.counter}'
        
        # Publish the message
        self.publisher_.publish(msg)
        
        # Log what we published
        self.get_logger().info(f'Publishing: "{msg.data}"')
        
        # Increment counter
        self.counter += 1


def main(args=None):
    """Main function to start the node"""
    # Initialize the ROS2 Python library
    rclpy.init(args=args)
    
    # Create our publisher node
    node = SimplePublisher()
    
    # Keep the node running (and calling callbacks)
    # This blocks until you press Ctrl+C
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    
    # Cleanup
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Code Explanation

Let's break down the key parts:

```python
class SimplePublisher(Node):
    def __init__(self):
        super().__init__('simple_publisher')
```
- Every ROS2 node is a class that inherits from `Node`
- We give it a name: `'simple_publisher'`

```python
self.publisher_ = self.create_publisher(String, 'chatter', 10)
```
- `String`: Message type we're publishing
- `'chatter'`: Topic name
- `10`: Queue size (buffer for messages)

```python
self.timer = self.create_timer(timer_period, self.timer_callback)
```
- Creates a timer that calls `timer_callback()` every `timer_period` seconds
- This is how we do periodic tasks in ROS2

```python
msg = String()
msg.data = f'Hello World: {self.counter}'
self.publisher_.publish(msg)
```
- Create a message
- Fill in the data
- Publish it!

```python
rclpy.spin(node)
```
- This keeps the node running and processing callbacks
- Without this, the program would exit immediately

---

## 👂 Subscriber Node: Listening to Messages

### The Code

Create `~/ros2_ws/src/my_first_pkg/my_first_pkg/simple_subscriber.py`:

```python
#!/usr/bin/env python3
"""
Simple Subscriber Node
Listens to /chatter topic and prints received messages
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimpleSubscriber(Node):
    """
    A simple subscriber node that receives messages.
    
    This demonstrates:
    - Creating a ROS2 node class
    - Creating a subscriber
    - Handling incoming messages with a callback
    """
    
    def __init__(self):
        # Initialize the node with a name
        super().__init__('simple_subscriber')
        
        # Create a subscriber
        # - Message type: String
        # - Topic name: '/chatter'
        # - Callback function: listener_callback
        # - Queue size: 10
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10
        )
        self.subscription  # prevent unused variable warning
        
        # Log that we've started
        self.get_logger().info('Simple Subscriber has started!')
    
    def listener_callback(self, msg):
        """
        This function is called every time a message arrives on /chatter.
        
        Args:
            msg (String): The received message
        """
        # Log what we received
        self.get_logger().info(f'I heard: "{msg.data}"')


def main(args=None):
    """Main function to start the node"""
    # Initialize the ROS2 Python library
    rclpy.init(args=args)
    
    # Create our subscriber node
    node = SimpleSubscriber()
    
    # Keep the node running (and calling callbacks)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    
    # Cleanup
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Code Explanation

```python
self.subscription = self.create_subscription(
    String,           # Message type
    'chatter',        # Topic name
    self.listener_callback,  # Function to call when message arrives
    10                # Queue size
)
```
- Subscribe to `chatter` topic
- When a message arrives, call `listener_callback()`

```python
def listener_callback(self, msg):
    self.get_logger().info(f'I heard: "{msg.data}"')
```
- This function is called automatically when a message arrives
- `msg` contains the received data
- We simply print it out

---

## ⚙️ Making Nodes Executable

### Step 1: Update `setup.py`

Edit `~/ros2_ws/src/my_first_pkg/setup.py` and add entry points:

```python
from setuptools import find_packages, setup

package_name = 'my_first_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='you@example.com',
    description='My first ROS2 package',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simple_publisher = my_first_pkg.simple_publisher:main',
            'simple_subscriber = my_first_pkg.simple_subscriber:main',
        ],
    },
)
```

The `entry_points` section tells ROS2:
- Create a command called `simple_publisher` that runs `simple_publisher.py`'s `main()` function
- Create a command called `simple_subscriber` that runs `simple_subscriber.py`'s `main()` function

---

## 🔨 Build and Run

### Step 1: Build Your Package

```bash
cd ~/ros2_ws
colcon build --packages-select my_first_pkg

# If successful, you'll see: "Finished <<< my_first_pkg"
```

### Step 2: Source Your Workspace

```bash
source ~/ros2_ws/install/setup.bash
```

**Important**: You need to source your workspace in every new terminal!

### Step 3: Run Publisher

**Terminal 1**:
```bash
ros2 run my_first_pkg simple_publisher
```

You should see:
```
[INFO] [simple_publisher]: Simple Publisher has started!
[INFO] [simple_publisher]: Publishing: "Hello World: 0"
[INFO] [simple_publisher]: Publishing: "Hello World: 1"
...
```

### Step 4: Run Subscriber

**Terminal 2**:
```bash
source ~/ros2_ws/install/setup.bash
ros2 run my_first_pkg simple_subscriber
```

You should see:
```
[INFO] [simple_subscriber]: Simple Subscriber has started!
[INFO] [simple_subscriber]: I heard: "Hello World: 5"
[INFO] [simple_subscriber]: I heard: "Hello World: 6"
...
```

🎉 **Success!** Your nodes are communicating!

---

## 🔍 Inspect Your System

With both nodes running, open **Terminal 3**:

```bash
source /opt/ros/jazzy/setup.bash

# See your nodes
ros2 node list
# /simple_publisher
# /simple_subscriber

# Get info about publisher
ros2 node info /simple_publisher

# See the topic
ros2 topic list
# /chatter

# Check publishing rate
ros2 topic hz /chatter
# Should be ~2 Hz (every 0.5 seconds)

# See the messages
ros2 topic echo /chatter
```

---

## 💡 Exercises

### Exercise 3.1: Modify Publishing Rate

Change the publisher to send messages every 1 second instead of 0.5 seconds.

**Hint**: Modify `timer_period` in `simple_publisher.py`

### Exercise 3.2: Change the Message

Make the publisher send your name instead of "Hello World".

### Exercise 3.3: Add a Counter to Subscriber

Make the subscriber keep track of how many messages it has received and print:
```
I heard message #5: "Hello World: 10"
```

### Exercise 3.4: Create a Number Publisher

Create a new node that publishes integers instead of strings:
1. Use message type `std_msgs/msg/Int32`
2. Topic name: `/number`
3. Publish incrementing numbers
4. Create a subscriber for it

**Hint**: Check message structure with:
```bash
ros2 interface show std_msgs/msg/Int32
```

---

## ✅ Tests

Run the automated tests:

```bash
cd ~/rostutorial/chapters/chapter_03_python_pubsub
python3 tests/test_chapter_03.py
```

This will:
- Verify your package builds correctly
- Test that your nodes run
- Check message flow
- Verify exercises are complete

---

## 🎯 Key Takeaways

1. **ROS2 nodes are classes** that inherit from `Node`
2. **Publishers** send messages periodically (or on events)
3. **Subscribers** receive messages through callbacks
4. **Timer callbacks** let you do things periodically
5. **colcon build** compiles your packages
6. **Source your workspace** to make nodes available
7. **Entry points** in setup.py make nodes executable

---

## 🐛 Common Issues

### "Package 'my_first_pkg' not found"
- Did you build? `colcon build --packages-select my_first_pkg`
- Did you source? `source ~/ros2_ws/install/setup.bash`

### "No module named 'rclpy'"
- Source ROS2: `source /opt/ros/jazzy/setup.bash`

### "Publisher not receiving"
- Are both nodes running?
- Check topic name matches: `ros2 topic list`
- Check message type matches

---

## 🚀 Next Chapter

Ready to see how C++ compares? In [Chapter 4](../chapter_04_cpp_pubsub/README.md), you'll create the same publisher/subscriber in C++ and learn when to use which language!

---

## 📚 Reference

### Common rclpy Functions

```python
# Node creation
super().__init__('node_name')

# Publisher
self.pub = self.create_publisher(MessageType, 'topic', 10)
self.pub.publish(msg)

# Subscriber
self.sub = self.create_subscription(MessageType, 'topic', callback, 10)

# Timer
self.timer = self.create_timer(period, callback)

# Logging
self.get_logger().info('message')
self.get_logger().warn('warning')
self.get_logger().error('error')
```
