# Chapter 16: Autonomous Navigation & Waypoint Following

**Goal**: Master advanced navigation techniques for reliable autonomous operation!

---

## 📖 Understanding Autonomous Navigation

**Autonomous** means the robot makes decisions by itself.

**Think of it like**:
- **Manual driving**: You control every move (teleop)
- **Autonomous driving**: Robot decides path and avoids obstacles (Nav2)

---

## 🎯 Basic Concepts Review

### What is a Waypoint?

A **waypoint** is a target location.

```python
# A waypoint is just an (x, y) position
waypoint = (3.0, 2.5)  # 3 meters east, 2.5 meters north

# With orientation (direction robot faces)
waypoint_with_heading = (3.0, 2.5, 1.57)  # Also face north (90°)
```

### What is a Goal?

A **goal** is where you want the robot to go.

In ROS2, goals are **actions** (long-running tasks with feedback).

---

## 🚀 Simple Waypoint Follower

### Understanding the Logic

Let's build a waypoint follower step by step:

```python
# Basic logic:
# 1. Have a list of waypoints
waypoints = [(1, 0), (2, 1), (3, 2)]

# 2. Keep track of where we are
current_waypoint = 0  # Start with first waypoint (index 0)

# 3. Send robot to current waypoint
# 4. When arrived, move to next
# 5. Repeat until all waypoints visited
```

---

### Complete Waypoint Follower Node

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from tf_transformations import quaternion_from_euler


class WaypointFollower(Node):
    """
    Follows a sequence of waypoints autonomously.
    
    This node sends waypoints one at a time to Nav2 and waits
    for completion before moving to the next.
    """
    
    def __init__(self):
        super().__init__('waypoint_follower')
        
        # List of waypoints (x, y, yaw)
        # You can load these from a file or parameter
        self.waypoints = [
            (1.0, 0.0, 0.0),      # Go east
            (2.0, 1.0, 1.57),     # Go northeast, face north
            (2.0, 2.0, 3.14),     # Go north, face west
            (0.0, 2.0, -1.57),    # Go west, face south
            (0.0, 0.0, 0.0),      # Return to start
        ]
        
        # Current position in waypoint list
        # Think of this like a bookmark in a book
        self.current_index = 0
        
        # Action client for navigation
        self.nav_client = ActionClient(
            self, NavigateToPose, 'navigate_to_pose')
        
        # Wait for Nav2 to be ready
        self.get_logger().info('Waiting for Nav2...')
        self.nav_client.wait_for_server()
        self.get_logger().info('Nav2 ready!')
        
        # Start following waypoints after 2 seconds
        self.create_timer(2.0, self.start_following)
    
    def start_following(self):
        """Begin following waypoints."""
        self.get_logger().info(
            f'Starting waypoint sequence ({len(self.waypoints)} waypoints)')
        self.send_next_waypoint()
    
    def send_next_waypoint(self):
        """Send the next waypoint to Nav2."""
        # Check if we've completed all waypoints
        if self.current_index >= len(self.waypoints):
            self.get_logger().info('✓ All waypoints completed!')
            return
        
        # Get current waypoint
        x, y, yaw = self.waypoints[self.current_index]
        
        self.get_logger().info(
            f'Going to waypoint {self.current_index + 1}/'
            f'{len(self.waypoints)}: ({x:.2f}, {y:.2f}, {yaw:.2f})')
        
        # Create goal message
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        
        # Set position
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.position.z = 0.0
        
        # Convert yaw (rotation) to quaternion
        # quaternion_from_euler converts (roll, pitch, yaw) to quaternion
        q = quaternion_from_euler(0, 0, yaw)
        goal.pose.pose.orientation.x = q[0]
        goal.pose.pose.orientation.y = q[1]
        goal.pose.pose.orientation.z = q[2]
        goal.pose.pose.orientation.w = q[3]
        
        # Send goal asynchronously (don't wait for it to finish)
        future = self.nav_client.send_goal_async(
            goal, feedback_callback=self.feedback_callback)
        
        # When goal is accepted, call goal_accepted_callback
        future.add_done_callback(self.goal_accepted_callback)
    
    def feedback_callback(self, feedback_msg):
        """
        Receive updates while robot is navigating.
        
        This is called repeatedly during navigation.
        """
        feedback = feedback_msg.feedback
        
        # feedback contains useful info:
        # - current_pose: where robot is now
        # - distance_remaining: how far to goal
        # - navigation_time: how long it's been navigating
        
        self.get_logger().info(
            f'Distance remaining: {feedback.distance_remaining:.2f}m',
            throttle_duration_sec=5.0)  # Only log every 5 seconds
    
    def goal_accepted_callback(self, future):
        """Called when Nav2 accepts or rejects goal."""
        goal_handle = future.result()
        
        # Check if goal was accepted
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected!')
            return
        
        self.get_logger().info('Goal accepted, navigating...')
        
        # Wait for navigation to complete
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.goal_completed_callback)
    
    def goal_completed_callback(self, future):
        """Called when robot reaches waypoint (or fails)."""
        result = future.result()
        
        # Check if navigation succeeded
        if result.status == 4:  # SUCCEEDED
            self.get_logger().info('✓ Waypoint reached!')
            
            # Move to next waypoint
            self.current_index += 1
            
            # Small pause before next waypoint
            self.create_timer(1.0, self.send_next_waypoint, oneshot=True)
        else:
            self.get_logger().error('✗ Navigation failed!')
            # Could retry here


def main(args=None):
    rclpy.init(args=args)
    node = WaypointFollower()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

## 📝 Loading Waypoints from File

**Better than hard-coding waypoints!**

### Create Waypoint File

`waypoints/patrol_route.yaml`:

```yaml
waypoints:
  - x: 1.0
    y: 0.0
    yaw: 0.0
    name: "Point A"
  
  - x: 2.0
    y: 1.0
    yaw: 1.57
    name: "Point B"
  
  - x: 2.0
    y: 2.0
    yaw: 3.14
    name: "Point C"
  
  - x: 0.0
    y: 0.0
    yaw: 0.0
    name: "Home"
```

---

### Load Waypoints in Node

```python
import yaml  # Library for reading YAML files
import os

class WaypointFollowerFromFile(Node):
    def __init__(self):
        super().__init__('waypoint_follower_from_file')
        
        # Parameter for waypoint file
        self.declare_parameter('waypoint_file', '')
        waypoint_file = self.get_parameter('waypoint_file').value
        
        # Load waypoints from file
        self.waypoints = self.load_waypoints(waypoint_file)
        
        self.get_logger().info(f'Loaded {len(self.waypoints)} waypoints')
        
        # ... rest of initialization
    
    def load_waypoints(self, filepath):
        """
        Read waypoints from YAML file.
        
        Returns list of (x, y, yaw, name) tuples.
        """
        # Check file exists
        if not os.path.exists(filepath):
            self.get_logger().error(f'File not found: {filepath}')
            return []
        
        # Open and read YAML file
        with open(filepath, 'r') as file:
            data = yaml.safe_load(file)
        
        # Convert to list of tuples
        waypoints = []
        for wp in data['waypoints']:
            # Extract values with defaults
            x = wp.get('x', 0.0)
            y = wp.get('y', 0.0)
            yaw = wp.get('yaw', 0.0)
            name = wp.get('name', 'Waypoint')
            
            waypoints.append((x, y, yaw, name))
        
        return waypoints
```

---

## 🔄 Looping Patrol

**Infinite patrol between waypoints**:

```python
class PatrolNode(Node):
    """Continuously patrol between waypoints."""
    
    def __init__(self):
        super().__init__('patrol_node')
        
        # Patrol waypoints
        self.waypoints = [
            (0.0, 0.0, 0.0),
            (2.0, 0.0, 0.0),
            (2.0, 2.0, 0.0),
            (0.0, 2.0, 0.0),
        ]
        
        self.current_index = 0
        self.patrol_count = 0  # How many loops completed
        
        # ... navigation setup
    
    def goal_completed_callback(self, future):
        """Move to next waypoint, loop if at end."""
        result = future.result()
        
        if result.status == 4:  # SUCCEEDED
            # Move to next waypoint
            self.current_index += 1
            
            # Check if we completed the loop
            if self.current_index >= len(self.waypoints):
                self.current_index = 0  # Start over!
                self.patrol_count += 1
                self.get_logger().info(
                    f'Completed patrol loop {self.patrol_count}')
            
            # Continue to next waypoint
            self.create_timer(1.0, self.send_next_waypoint, oneshot=True)
```

---

## 🛑 Canceling Navigation

**Stop robot mid-navigation**:

```python
class CancelableNavigator(Node):
    def __init__(self):
        super().__init__('cancelable_navigator')
        
        # ... setup navigation client
        
        # Subscribe to emergency stop button
        self.create_subscription(
            Bool, '/emergency_stop', self.emergency_callback, 10)
        
        self.current_goal_handle = None
    
    def send_goal(self, x, y, yaw):
        """Send navigation goal and store handle."""
        goal = NavigateToPose.Goal()
        # ... setup goal
        
        future = self.nav_client.send_goal_async(goal)
        future.add_done_callback(self.goal_response_callback)
    
    def goal_response_callback(self, future):
        """Store goal handle for later cancellation."""
        self.current_goal_handle = future.result()
    
    def emergency_callback(self, msg):
        """Cancel navigation on emergency stop."""
        if msg.data and self.current_goal_handle is not None:
            self.get_logger().warn('EMERGENCY STOP - Canceling navigation!')
            
            # Cancel current goal
            cancel_future = self.current_goal_handle.cancel_goal_async()
            cancel_future.add_done_callback(self.cancel_done_callback)
    
    def cancel_done_callback(self, future):
        """Called when cancellation completes."""
        self.get_logger().info('Navigation canceled')
        self.current_goal_handle = None
```

---

## 🎯 Dynamic Waypoint Addition

**Add waypoints while running**:

```python
from my_robot_interfaces.srv import AddWaypoint  # Custom service

class DynamicWaypointFollower(Node):
    def __init__(self):
        super().__init__('dynamic_waypoint_follower')
        
        # Start with empty waypoint list
        self.waypoints = []
        self.current_index = 0
        
        # Service to add waypoints
        self.srv = self.create_service(
            AddWaypoint,
            '/add_waypoint',
            self.add_waypoint_callback)
        
        # ... navigation setup
    
    def add_waypoint_callback(self, request, response):
        """Service to add new waypoint."""
        # Add waypoint to list
        new_wp = (request.x, request.y, request.yaw)
        self.waypoints.append(new_wp)
        
        self.get_logger().info(
            f'Added waypoint: ({request.x}, {request.y}, {request.yaw})')
        
        # If not currently navigating, start
        if self.current_index >= len(self.waypoints) - 1:
            self.send_next_waypoint()
        
        response.success = True
        response.message = f'Waypoint added (total: {len(self.waypoints)})'
        return response
```

---

## 💻 Exercises

### Exercise 16.1: Figure-8 Pattern

Create waypoints that make robot drive in figure-8 shape.

### Exercise 16.2: Conditional Waypoints

Skip waypoints based on battery level:
```python
if battery_percentage < 20:
    go_to_charging_station()
```

### Exercise 16.3: Interactive Waypoint Tool

Create a simple GUI to click waypoints on a map.

**Hint**: Use RViz's "Publish Point" feature!

---

## 🎯 Key Takeaways

1. **Waypoint following** navigates through a sequence
2. **Action clients** send navigation goals
3. **Callbacks** handle goal acceptance, feedback, and completion
4. **YAML files** store waypoint data
5. **Cancellation** stops mid-navigation
6. **Loops** create patrol patterns

---

## 🚀 Next Chapter

[Chapter 17: Behavior Trees](../chapter_17_behavior_trees/README.md) - Coordinate complex robot behaviors!

---

## 📚 Resources

- [Nav2 Actions](https://docs.nav2.org/concepts/index.html#actions)
- [Python YAML](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [Action Client Tutorial](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Writing-an-Action-Server-Client/Py.html)
