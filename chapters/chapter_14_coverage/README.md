# Chapter 14: Coverage Path Planning for Cleaning Robots

**Goal**: Learn algorithms to systematically cover entire areas - essential for cleaning robots!

---

## 📖 What is Coverage Path Planning?

**Coverage** means visiting every point in an area.

**Examples**:
- Vacuum cleaner covering entire room
- Lawn mower cutting entire lawn
- Agricultural robot covering field

**Different from navigation**: Navigation goes from A to B. Coverage visits EVERYTHING.

---

## 🎯 Basic Programming: Understanding Algorithms

### What is an Algorithm?

An **algorithm** is a step-by-step recipe to solve a problem.

**Example - Making Toast** (algorithm):
1. Get bread
2. Put in toaster
3. Wait 2 minutes
4. Remove toast
5. Done!

**Example - Covering a Room** (algorithm):
1. Start at corner
2. Move forward until wall
3. Move sideways one robot-width
4. Move forward (opposite direction)
5. Repeat until room covered

---

## 🌊 Basic Pattern: Boustrophedon (Back-and-Forth)

**"Boustrophedon"** = Greek for "ox-turning" (like plowing a field)

```
Start→ ────────────→
         ←────────────
       ────────────→
         ←────────────  End
```

**Advantages**:
- Simple!
- Predictable
- Complete coverage

**Disadvantages**:
- Lots of turns
- May revisit areas

---

## 💻 Simple Coverage Algorithm (Python)

### Understanding the Code

Let's build a basic coverage planner step by step:

```python
import math

# First, understand basic concepts:

# 1. VARIABLES - Store information
robot_width = 0.4  # meters
room_width = 5.0   # meters  
room_height = 4.0  # meters

# 2. LISTS - Store multiple values
waypoints = []  # Empty list to hold (x, y) positions

# 3. FOR LOOP - Repeat actions
# This will repeat the code inside for each 'row'
num_rows = int(room_height / robot_width)  # How many rows?

for row in range(num_rows):  # row = 0, then 1, then 2, etc.
    # 4. IF/ELSE - Make decisions
    if row % 2 == 0:  # Even rows (0, 2, 4...)
        # Go left to right
        start_x = 0
        end_x = room_width
    else:  # Odd rows (1, 3, 5...)
        # Go right to left
        start_x = room_width
        end_x = 0
    
    # Calculate Y position for this row
    y = row * robot_width
    
    # Add waypoints to our list
    waypoints.append((start_x, y))
    waypoints.append((end_x, y))

# Now waypoints contains all positions to visit!
print(f"Generated {len(waypoints)} waypoints")
```

---

## 🤖 Complete Coverage Node

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient


class SimpleCoverageNode(Node):
    """
    Generates and executes a simple coverage pattern.
    
    This node creates a back-and-forth pattern and sends each
    waypoint to Nav2 for navigation.
    """
    
    def __init__(self):
        super().__init__('simple_coverage_node')
        
        # Parameters for the area to cover
        self.declare_parameter('area_width', 5.0)   # meters
        self.declare_parameter('area_height', 4.0)  # meters
        self.declare_parameter('robot_width', 0.4)  # meters
        self.declare_parameter('start_x', 0.0)      # Starting corner
        self.declare_parameter('start_y', 0.0)
        
        # Get parameter values
        area_width = self.get_parameter('area_width').value
        area_height = self.get_parameter('area_height').value
        robot_width = self.get_parameter('robot_width').value
        start_x = self.get_parameter('start_x').value
        start_y = self.get_parameter('start_y').value
        
        # Generate coverage pattern
        self.waypoints = self.generate_coverage_pattern(
            area_width, area_height, robot_width, start_x, start_y)
        
        self.get_logger().info(f'Generated {len(self.waypoints)} waypoints')
        
        # Action client for navigation
        self.nav_client = ActionClient(
            self, NavigateToPose, 'navigate_to_pose')
        
        # Track current waypoint
        self.current_waypoint_index = 0
        
        # Start coverage after 2 seconds
        self.create_timer(2.0, self.start_coverage)
    
    def generate_coverage_pattern(self, width, height, robot_width, 
                                  start_x, start_y):
        """
        Generate back-and-forth coverage pattern.
        
        Returns list of (x, y) tuples representing waypoints.
        """
        waypoints = []
        
        # Calculate number of rows needed
        # int() converts decimal to whole number
        num_rows = int(height / robot_width)
        
        # Generate waypoints for each row
        for row in range(num_rows):
            # Calculate y position for this row
            y = start_y + (row * robot_width)
            
            # Alternate direction each row
            if row % 2 == 0:  # Even rows: left to right
                x_start = start_x
                x_end = start_x + width
            else:  # Odd rows: right to left
                x_start = start_x + width
                x_end = start_x
            
            # Add start and end of row
            waypoints.append((x_start, y))
            waypoints.append((x_end, y))
        
        return waypoints
    
    def start_coverage(self):
        """Start executing coverage pattern."""
        if self.current_waypoint_index < len(self.waypoints):
            self.navigate_to_next_waypoint()
        else:
            self.get_logger().info('Coverage complete!')
    
    def navigate_to_next_waypoint(self):
        """Send next waypoint to navigation."""
        # Get next waypoint
        x, y = self.waypoints[self.current_waypoint_index]
        
        self.get_logger().info(
            f'Navigating to waypoint {self.current_waypoint_index + 1}/'
            f'{len(self.waypoints)}: ({x:.2f}, {y:.2f})')
        
        # Create navigation goal
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0
        
        # Orientation (facing forward)
        goal_msg.pose.pose.orientation.w = 1.0
        
        # Send goal
        self.nav_client.wait_for_server()
        send_goal_future = self.nav_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_accepted_callback)
    
    def goal_accepted_callback(self, future):
        """Called when navigation goal is accepted."""
        goal_handle = future.result()
        
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected!')
            return
        
        # Wait for result
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.goal_completed_callback)
    
    def goal_completed_callback(self, future):
        """Called when waypoint is reached."""
        self.get_logger().info('Waypoint reached!')
        
        # Move to next waypoint
        self.current_waypoint_index += 1
        
        # Small delay before next waypoint
        self.create_timer(0.5, self.continue_coverage, oneshot=True)
    
    def continue_coverage(self):
        """Continue to next waypoint."""
        if self.current_waypoint_index < len(self.waypoints):
            self.navigate_to_next_waypoint()
        else:
            self.get_logger().info('✓ Coverage pattern complete!')


def main(args=None):
    rclpy.init(args=args)
    node = SimpleCoverageNode()
    
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

## 🎨 Visualizing Coverage Path

```python
import matplotlib.pyplot as plt

def visualize_coverage_path(waypoints, room_width, room_height):
    """
    Draw the coverage path.
    
    This helps you see the pattern before running it!
    """
    # Extract x and y coordinates
    # List comprehension: [expression for item in list]
    xs = [wp[0] for wp in waypoints]  # Get all x values
    ys = [wp[1] for wp in waypoints]  # Get all y values
    
    # Create plot
    plt.figure(figsize=(10, 8))
    
    # Draw room boundary
    plt.plot([0, room_width, room_width, 0, 0], 
             [0, 0, room_height, room_height, 0],
             'k-', linewidth=2, label='Room')
    
    # Draw coverage path
    plt.plot(xs, ys, 'b-', linewidth=1, label='Path')
    
    # Mark waypoints
    plt.plot(xs, ys, 'ro', markersize=5)
    
    # Mark start and end
    plt.plot(xs[0], ys[0], 'go', markersize=10, label='Start')
    plt.plot(xs[-1], ys[-1], 'rs', markersize=10, label='End')
    
    plt.xlabel('X (meters)')
    plt.ylabel('Y (meters)')
    plt.title('Coverage Path')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    
    # Save to file
    plt.savefig('coverage_path.png')
    print("Saved path visualization to coverage_path.png")
    
    # Show plot
    plt.show()


# Example usage:
waypoints = [(0, 0), (5, 0), (5, 0.4), (0, 0.4), (0, 0.8), (5, 0.8)]
visualize_coverage_path(waypoints, 5.0, 4.0)
```

---

## 🔄 Advanced Pattern: Spiral Coverage

```python
def generate_spiral_pattern(width, height, robot_width):
    """
    Generate spiral coverage (from outside to center).
    
    Think of it like a spiral notebook!
    """
    waypoints = []
    
    # Start at outer edge
    x_min, x_max = 0, width
    y_min, y_max = 0, height
    
    # Keep spiraling inward
    while x_max - x_min > robot_width and y_max - y_min > robot_width:
        # Top edge (left to right)
        waypoints.append((x_min, y_max))
        waypoints.append((x_max, y_max))
        
        # Right edge (top to bottom)
        waypoints.append((x_max, y_max))
        waypoints.append((x_max, y_min))
        
        # Bottom edge (right to left)
        waypoints.append((x_max, y_min))
        waypoints.append((x_min, y_min))
        
        # Left edge (bottom to top)
        waypoints.append((x_min, y_min))
        waypoints.append((x_min, y_max))
        
        # Shrink bounds for next spiral
        x_min += robot_width
        x_max -= robot_width
        y_min += robot_width
        y_max -= robot_width
    
    return waypoints
```

---

## 📊 Coverage Metrics

```python
class CoverageMetrics(Node):
    """Track coverage performance."""
    
    def __init__(self):
        super().__init__('coverage_metrics')
        
        # Metrics
        self.waypoints_completed = 0
        self.total_waypoints = 0
        self.total_distance = 0.0
        self.start_time = self.get_clock().now()
        
        # Subscribe to robot position
        self.create_subscription(
            PoseStamped, '/robot_pose', self.pose_callback, 10)
        
        self.last_position = None
    
    def pose_callback(self, msg):
        """Track distance traveled."""
        if self.last_position is not None:
            # Calculate distance between positions
            dx = msg.pose.position.x - self.last_position.x
            dy = msg.pose.position.y - self.last_position.y
            
            # Pythagorean theorem: distance = sqrt(dx^2 + dy^2)
            distance = math.sqrt(dx**2 + dy**2)
            
            self.total_distance += distance
        
        self.last_position = msg.pose.position
    
    def waypoint_reached(self):
        """Call when waypoint is completed."""
        self.waypoints_completed += 1
        
        # Calculate progress
        progress = (self.waypoints_completed / self.total_waypoints) * 100
        
        self.get_logger().info(
            f'Progress: {progress:.1f}% '
            f'({self.waypoints_completed}/{self.total_waypoints})')
    
    def print_summary(self):
        """Print final statistics."""
        elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
        
        print("\n" + "="*50)
        print("Coverage Summary")
        print("="*50)
        print(f"Waypoints completed: {self.waypoints_completed}/{self.total_waypoints}")
        print(f"Total distance: {self.total_distance:.2f} meters")
        print(f"Time elapsed: {elapsed:.1f} seconds")
        print(f"Average speed: {self.total_distance/elapsed:.2f} m/s")
        print("="*50 + "\n")
```

---

## 💻 Exercises

### Exercise 14.1: Custom Area

Create coverage pattern for your room:
1. Measure room dimensions
2. Set robot width
3. Generate and visualize pattern

### Exercise 14.2: Obstacle Avoidance

Modify pattern to skip known obstacles:
```python
obstacles = [(2, 2, 0.5)]  # (x, y, radius)
# Skip waypoints inside obstacles
```

### Exercise 14.3: Optimize Path

Calculate which pattern uses less distance:
- Boustrophedon
- Spiral

---

## 🎯 Key Takeaways

1. **Coverage** visits all points in an area
2. **Boustrophedon** (back-and-forth) is simplest
3. **Algorithms** are step-by-step instructions
4. **Loops** repeat actions (essential for coverage)
5. **Lists** store waypoints
6. **Metrics** track performance

---

## 🚀 Next Chapter

[Chapter 16: Autonomous Navigation](../chapter_16_autonomous_nav/README.md) - Advanced waypoint following and recovery behaviors!

---

## 📚 Resources

- [Coverage Path Planning Survey](https://arxiv.org/abs/1908.09630)
- [matplotlib Documentation](https://matplotlib.org/)
- [Python Lists Tutorial](https://docs.python.org/3/tutorial/datastructures.html)
