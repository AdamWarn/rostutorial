# Chapter 7: Gazebo Simulation Basics

**Goal**: Simulate your robot in a 3D physics environment using Gazebo.

---

## 📖 What is Gazebo?

**Gazebo** is a 3D robot simulator that provides:
- **Physics engine**: Gravity, collisions, friction
- **Sensors**: LiDAR, cameras, IMU, GPS
- **Actuators**: Motors, servos
- **Environments**: Buildings, outdoor scenes
- **Realistic simulation**: Test before deploying to real hardware

---

## 🎯 From URDF to Gazebo

Your URDF from Chapter 6 needs **Gazebo-specific tags** to work in simulation.

### Adding Gazebo Properties

```xml
<?xml version="1.0"?>
<robot name="simple_robot">
  
  <!-- Include your URDF from Chapter 6 here -->
  
  <!-- Gazebo-specific properties -->
  
  <!-- Add colors (Gazebo uses different materials than RViz) -->
  <gazebo reference="base_link">
    <material>Gazebo/Blue</material>
  </gazebo>
  
  <gazebo reference="left_wheel">
    <material>Gazebo/Black</material>
    <mu1>1.0</mu1>  <!-- friction coefficient -->
    <mu2>1.0</mu2>
  </gazebo>
  
  <gazebo reference="right_wheel">
    <material>Gazebo/Black</material>
    <mu1>1.0</mu1>
    <mu2>1.0</mu2>
  </gazebo>
  
  <gazebo reference="caster_wheel">
    <material>Gazebo/Gray</material>
    <mu1>0.1</mu1>  <!-- low friction for caster -->
    <mu2>0.1</mu2>
  </gazebo>
  
  <gazebo reference="lidar_link">
    <material>Gazebo/Red</material>
  </gazebo>
  
  <!-- Differential Drive Plugin (makes wheels move!) -->
  <gazebo>
    <plugin name="diff_drive" filename="libgazebo_ros_diff_drive.so">
      <!-- Wheel joints -->
      <left_joint>left_wheel_joint</left_joint>
      <right_joint>right_wheel_joint</right_joint>
      
      <!-- Kinematics -->
      <wheel_separation>0.45</wheel_separation>
      <wheel_diameter>0.2</wheel_diameter>
      
      <!-- Limits -->
      <max_wheel_torque>20</max_wheel_torque>
      <max_wheel_acceleration>1.0</max_wheel_acceleration>
      
      <!-- Input/Output -->
      <command_topic>cmd_vel</command_topic>
      <publish_odom>true</publish_odom>
      <publish_odom_tf>true</publish_odom_tf>
      <publish_wheel_tf>false</publish_wheel_tf>
      
      <odometry_topic>odom</odometry_topic>
      <odometry_frame>odom</odometry_frame>
      <robot_base_frame>base_link</robot_base_frame>
      
      <!-- Update rate -->
      <update_rate>50</update_rate>
    </plugin>
  </gazebo>
  
  <!-- LiDAR Sensor Plugin -->
  <gazebo reference="lidar_link">
    <sensor name="lidar" type="ray">
      <always_on>true</always_on>
      <update_rate>10</update_rate>
      <visualize>true</visualize>
      
      <ray>
        <scan>
          <horizontal>
            <samples>360</samples>
            <resolution>1</resolution>
            <min_angle>-3.14159</min_angle>
            <max_angle>3.14159</max_angle>
          </horizontal>
        </scan>
        <range>
          <min>0.12</min>
          <max>10.0</max>
          <resolution>0.01</resolution>
        </range>
      </ray>
      
      <plugin name="scan" filename="libgazebo_ros_ray_sensor.so">
        <ros>
          <remapping>~/out:=scan</remapping>
        </ros>
        <output_type>sensor_msgs/LaserScan</output_type>
        <frame_name>lidar_link</frame_name>
      </plugin>
    </sensor>
  </gazebo>
  
</robot>
```

---

## 🚀 Launching Your Robot in Gazebo

### Step 1: Create Launch File

**File**: `~/ros2_ws/src/my_robot_description/launch/gazebo.launch.py`

```python
import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    
    # Get package directory
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_my_robot = get_package_share_directory('my_robot_description')
    
    # URDF file path
    urdf_file = os.path.join(pkg_my_robot, 'urdf', 'simple_robot.urdf')
    
    # Read URDF
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()
    
    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py'),
        )
    )
    
    # Spawn robot
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description',
                   '-entity', 'simple_robot'],
        output='screen'
    )
    
    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}]
    )
    
    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
    ])
```

### Step 2: Install Launch Files

Update `setup.py`:

```python
import os
from glob import glob
from setuptools import setup

package_name = 'my_robot_description'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='you@example.com',
    description='Robot description package',
    license='Apache-2.0',
    tests_require=['pytest'],
)
```

### Step 3: Build and Launch

```bash
cd ~/ros2_ws
colcon build --packages-select my_robot_description
source install/setup.bash

# Launch Gazebo with your robot!
ros2 launch my_robot_description gazebo.launch.py
```

---

## 🎮 Controlling Your Robot

Once Gazebo is running, control your robot:

```bash
# Keyboard control
sudo apt install ros-jazzy-teleop-twist-keyboard
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# Or publish velocity commands directly
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.5}, angular: {z: 0.3}}"
```

**Controls**:
- `i`: Forward
- `k`: Stop
- `j`: Turn left
- `l`: Turn right

---

## 🗺️ Adding Worlds and Obstacles

### Create a World File

**File**: `~/ros2_ws/src/my_robot_description/worlds/simple_world.world`

```xml
<?xml version="1.0"?>
<sdf version="1.6">
  <world name="simple_world">
    
    <!-- Sun (lighting) -->
    <include>
      <uri>model://sun</uri>
    </include>
    
    <!-- Ground plane -->
    <include>
      <uri>model://ground_plane</uri>
    </include>
    
    <!-- Walls to create a room -->
    <model name="wall_1">
      <static>true</static>
      <pose>5 0 1 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.2 10 2</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.2 10 2</size>
            </box>
          </geometry>
          <material>
            <ambient>0.5 0.5 0.5 1</ambient>
          </material>
        </visual>
      </link>
    </model>
    
    <!-- Add more walls, obstacles, etc. -->
    
  </world>
</sdf>
```

### Use Custom World in Launch File

```python
# In gazebo.launch.py, modify gazebo launch:
gazebo = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
        os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py'),
    ),
    launch_arguments={
        'world': os.path.join(pkg_my_robot, 'worlds', 'simple_world.world')
    }.items()
)
```

---

## 💻 Exercises

### Exercise 7.1: Drive Your Robot
1. Launch Gazebo with your robot
2. Use keyboard teleop to drive around
3. Use `ros2 topic echo /scan` to see LiDAR data
4. Use `ros2 topic echo /odom` to see odometry

### Exercise 7.2: Create an Obstacle Course
Add walls and obstacles to your world file. Navigate through them!

### Exercise 7.3: Add a Camera
Add a camera sensor to your robot:

```xml
<gazebo reference="camera_link">
  <sensor name="camera" type="camera">
    <always_on>true</always_on>
    <update_rate>30</update_rate>
    <camera>
      <horizontal_fov>1.047</horizontal_fov>
      <image>
        <width>640</width>
        <height>480</height>
      </image>
    </camera>
    <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
      <ros>
        <remapping>~/image_raw:=camera/image_raw</remapping>
      </ros>
      <camera_name>camera</camera_name>
      <frame_name>camera_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

View camera: `ros2 run rqt_image_view rqt_image_view`

---

## 🎯 Common Gazebo Plugins

| Plugin | Purpose | Topic |
|--------|---------|-------|
| `gazebo_ros_diff_drive` | Differential drive | `/cmd_vel`, `/odom` |
| `gazebo_ros_ray_sensor` | LiDAR | `/scan` |
| `gazebo_ros_camera` | Camera | `/camera/image_raw` |
| `gazebo_ros_imu_sensor` | IMU | `/imu` |
| `gazebo_ros_gps_sensor` | GPS | `/gps/fix` |

---

## 🐛 Troubleshooting

### "Gazebo crashes on startup"
```bash
# Reset Gazebo
killall gzserver gzclient
rm -rf ~/.gazebo
```

### "Robot falls through ground"
- Check collision geometry exists
- Verify inertial properties are set
- Ground plane must be present in world

### "Wheels don't move"
- Check joint names in diff_drive plugin match URDF
- Verify wheel separation and diameter are correct
- Check `/cmd_vel` topic is being published

### "LiDAR shows no data"
- Verify LiDAR link has correct sensor plugin
- Check sensor is not inside another link (collision)
- Use `ros2 topic list` to confirm `/scan` exists

---

## 🎯 Key Takeaways

- Gazebo simulates physics and sensors
- URDF needs Gazebo plugins for functionality
- Differential drive plugin makes robot move
- Sensor plugins publish to ROS topics
- World files define environment
- Test everything in simulation first!

---

## 🚀 Next Chapter

[Chapter 8: TF2 - Coordinate Frames](../chapter_08_tf2/README.md) - Learn how ROS tracks where everything is in 3D space!

---

## 📚 Resources

- [Gazebo ROS2 Tutorials](https://gazebosim.org/docs/latest/ros2_integration)
- [Gazebo Plugins](https://classic.gazebosim.org/tutorials?tut=ros_gzplugins)
- [SDF Format](http://sdformat.org/)
