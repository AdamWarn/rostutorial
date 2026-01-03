# Chapter 15: Path Planning & Costmaps

**Goal**: Plan collision-free paths and navigate autonomously with Nav2!

---

## 📖 What is Nav2?

**Nav2 (Navigation2)** is ROS2's complete autonomous navigation system.

**It provides**:
- Path planning algorithms
- Obstacle avoidance
- Costmaps (inflated obstacle maps)
- Recovery behaviors
- Waypoint following

---

## 🗺️ Costmaps

**Costmaps** add safety margins around obstacles.

```
Regular Map:        Costmap:
[  ][  ][█]        [50][99][█]
[  ][  ][  ]   =>  [25][50][99]
[  ][  ][  ]       [  ][25][50]

Legend:
█ = occupied (255)
Numbers = inflation (0-254)
```

**Purpose**: Keep robot center away from walls!

---

## 🎯 Installing Nav2

```bash
sudo apt install ros-jazzy-navigation2 ros-jazzy-nav2-bringup
```

---

## ⚙️ Costmap Configuration

### Global Costmap (for planning)

`config/global_costmap_params.yaml`:

```yaml
global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 1.0
      global_frame: map
      robot_base_frame: base_link
      use_sim_time: True
      robot_radius: 0.22  # meters
      resolution: 0.05
      track_unknown_space: true
      
      plugins: ["static_layer", "inflation_layer"]
      
      static_layer:
        plugin: "nav2_costmap_2d::StaticLayer"
        map_subscribe_transient_local: True
      
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55
```

---

### Local Costmap (for obstacle avoidance)

`config/local_costmap_params.yaml`:

```yaml
local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 5.0
      publish_frequency: 2.0
      global_frame: odom
      robot_base_frame: base_link
      use_sim_time: True
      rolling_window: true
      width: 3  # meters
      height: 3
      resolution: 0.05
      robot_radius: 0.22
      
      plugins: ["obstacle_layer", "inflation_layer"]
      
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        enabled: True
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "LaserScan"
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0
      
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55
```

---

## 🛤️ Path Planners

### NavFn Planner (Dijkstra-based)

`config/planner_params.yaml`:

```yaml
planner_server:
  ros__parameters:
    expected_planner_frequency: 20.0
    use_sim_time: True
    planner_plugins: ["GridBased"]
    
    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.5
      use_astar: false  # Use Dijkstra
      allow_unknown: true
```

---

### Smac Planner (Hybrid A*)

```yaml
planner_server:
  ros__parameters:
    planner_plugins: ["GridBased"]
    
    GridBased:
      plugin: "nav2_smac_planner/SmacPlanner2D"
      tolerance: 0.5
      downsample_costmap: false
      downsampling_factor: 1
      allow_unknown: true
      max_iterations: 1000000
      max_on_approach_iterations: 1000
      max_planning_time: 5.0
      motion_model_for_search: "MOORE"  # or "VON_NEUMANN", "DUBIN", "REEDS_SHEPP"
      cost_travel_multiplier: 2.0
```

---

## 🚗 Controller (Path Following)

### DWB Controller

`config/controller_params.yaml`:

```yaml
controller_server:
  ros__parameters:
    use_sim_time: True
    controller_frequency: 20.0
    min_x_velocity_threshold: 0.001
    min_y_velocity_threshold: 0.5
    min_theta_velocity_threshold: 0.001
    progress_checker_plugins: ["progress_checker"]
    goal_checker_plugins: ["goal_checker"]
    controller_plugins: ["FollowPath"]
    
    progress_checker:
      plugin: "nav2_controller::SimpleProgressChecker"
      required_movement_radius: 0.5
      movement_time_allowance: 10.0
    
    goal_checker:
      plugin: "nav2_controller::SimpleGoalChecker"
      xy_goal_tolerance: 0.25
      yaw_goal_tolerance: 0.25
      stateful: True
    
    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"
      debug_trajectory_details: True
      min_vel_x: 0.0
      min_vel_y: 0.0
      max_vel_x: 0.26
      max_vel_y: 0.0
      max_vel_theta: 1.0
      min_speed_xy: 0.0
      max_speed_xy: 0.26
      min_speed_theta: 0.0
      acc_lim_x: 2.5
      acc_lim_y: 0.0
      acc_lim_theta: 3.2
      decel_lim_x: -2.5
      decel_lim_y: 0.0
      decel_lim_theta: -3.2
      vx_samples: 20
      vy_samples: 0
      vth_samples: 40
      sim_time: 1.7
      linear_granularity: 0.05
      angular_granularity: 0.025
      transform_tolerance: 0.2
      critics: ["RotateToGoal", "Oscillation", "BaseObstacle", "GoalAlign", "PathAlign", "PathDist", "GoalDist"]
```

---

## 🚀 Complete Nav2 Launch

`launch/navigation.launch.py`:

```python
import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_dir = get_package_share_directory('my_robot_navigation')
    
    use_sim_time = LaunchConfiguration('use_sim_time')
    map_file = LaunchConfiguration('map')
    
    # Config files
    global_costmap_params = os.path.join(pkg_dir, 'config', 'global_costmap_params.yaml')
    local_costmap_params = os.path.join(pkg_dir, 'config', 'local_costmap_params.yaml')
    planner_params = os.path.join(pkg_dir, 'config', 'planner_params.yaml')
    controller_params = os.path.join(pkg_dir, 'config', 'controller_params.yaml')
    
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('map', default_value=os.path.join(pkg_dir, 'maps', 'my_map.yaml')),
        
        # Map Server
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            parameters=[{'yaml_filename': map_file}, {'use_sim_time': use_sim_time}]
        ),
        
        # AMCL
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            parameters=[{
                'use_sim_time': use_sim_time,
                'base_frame_id': 'base_link',
                'odom_frame_id': 'odom',
                'global_frame_id': 'map',
            }]
        ),
        
        # Planner Server
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            parameters=[planner_params, global_costmap_params, {'use_sim_time': use_sim_time}]
        ),
        
        # Controller Server
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            parameters=[controller_params, local_costmap_params, {'use_sim_time': use_sim_time}]
        ),
        
        # Behavior Server (recovery behaviors)
        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            parameters=[{'use_sim_time': use_sim_time}]
        ),
        
        # BT Navigator (coordinates everything)
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            parameters=[{'use_sim_time': use_sim_time}]
        ),
        
        # Lifecycle Manager
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            parameters=[{
                'node_names': [
                    'map_server',
                    'amcl',
                    'planner_server',
                    'controller_server',
                    'behavior_server',
                    'bt_navigator'
                ],
                'autostart': True,
                'use_sim_time': use_sim_time
            }]
        ),
    ])
```

---

## 🎯 Sending Navigation Goals

### Method 1: RViz

1. Open RViz
2. Add Nav2 panels
3. Click "Navigation2 Goal" button
4. Click target pose on map

---

### Method 2: Command Line

```bash
ros2 topic pub --once /goal_pose geometry_msgs/PoseStamped "
{
  header: {frame_id: 'map'},
  pose: {
    position: {x: 2.0, y: 1.0, z: 0.0},
    orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
  }
}"
```

---

### Method 3: Action Client (Recommended)

```python
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient

class NavigationClient(Node):
    def __init__(self):
        super().__init__('navigation_client')
        
        self.action_client = ActionClient(
            self,
            NavigateToPose,
            'navigate_to_pose')
    
    def send_goal(self, x, y, yaw=0.0):
        """Send navigation goal."""
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0
        
        # Convert yaw to quaternion
        from tf_transformations import quaternion_from_euler
        q = quaternion_from_euler(0, 0, yaw)
        goal_msg.pose.pose.orientation.x = q[0]
        goal_msg.pose.pose.orientation.y = q[1]
        goal_msg.pose.pose.orientation.z = q[2]
        goal_msg.pose.pose.orientation.w = q[3]
        
        self.get_logger().info(f'Sending goal: ({x}, {y})')
        
        # Wait for server
        self.action_client.wait_for_server()
        
        # Send goal with callbacks
        self._send_goal_future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback)
        
        self._send_goal_future.add_done_callback(self.goal_response_callback)
    
    def goal_response_callback(self, future):
        goal_handle = future.result()
        
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected!')
            return
        
        self.get_logger().info('Goal accepted!')
        
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)
    
    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info('Navigation complete!')
    
    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        # Can access current_pose, distance_remaining, etc.
        self.get_logger().info(
            f'Distance remaining: {feedback.distance_remaining:.2f}m',
            throttle_duration_sec=5.0)
```

---

## 📊 Visualizing in RViz

**Essential displays**:
- Map (`/map`)
- LaserScan (`/scan`)
- Local Costmap (`/local_costmap/costmap`)
- Global Costmap (`/global_costmap/costmap`)
- Global Plan (`/plan`)
- Local Plan (`/local_plan`)
- TF
- RobotModel

---

## 🐛 Troubleshooting

### "No path found"
- Check global costmap - is path obstructed?
- Increase `tolerance` in planner config
- Check `allow_unknown: true`

### Robot not moving
- Check controller server running
- Verify `/cmd_vel` topic published
- Check velocity limits in config

### Robot oscillates
- Tune DWB critics weights
- Reduce `vx_samples` / `vth_samples`
- Adjust `sim_time`

### Crashes into obstacles
- Increase `inflation_radius`
- Check `robot_radius` is correct
- Verify LiDAR data: `ros2 topic echo /scan`

---

## 💻 Exercises

### Exercise 15.1: Waypoint Navigation

Create a node that navigates through multiple waypoints:

```python
waypoints = [
    (1.0, 0.0, 0.0),
    (2.0, 1.0, 1.57),
    (1.0, 2.0, 3.14),
    (0.0, 0.0, 0.0),
]

# Navigate to each waypoint in sequence
```

### Exercise 15.2: Patrol Mode

Create an infinite patrol between two points.

### Exercise 15.3: Goal Cancellation

Implement a safety node that cancels navigation if battery is low.

---

## 🎯 Key Takeaways

1. **Costmaps** inflate obstacles for safety
2. **Global planner** finds path on full map
3. **Local planner** avoids dynamic obstacles
4. **DWB controller** generates velocity commands
5. **Action interface** for navigation goals
6. **Behavior trees** coordinate all components

---

## 🚀 Next Chapter

[Chapter 16: Autonomous Navigation](../chapter_16_autonomous_nav/README.md) - Advanced waypoint following and goal handling!

---

## 📚 Resources

- [Nav2 Documentation](https://docs.nav2.org/)
- [Costmap2D](https://docs.nav2.org/configuration/packages/configuring-costmaps.html)
- [DWB Controller](https://docs.nav2.org/configuration/packages/configuring-dwb-controller.html)
- [Tuning Guide](https://docs.nav2.org/tuning/index.html)
