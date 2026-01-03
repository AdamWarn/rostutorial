# 🔧 Troubleshooting Guide

**Common issues and solutions for ROS2 Jazzy SLAM Robot course**

---

## 🚨 Installation Issues

### **Issue: "ros2: command not found"**

**Symptoms:**
```bash
$ ros2
bash: ros2: command not found
```

**Solutions:**

1. **Source ROS2 environment:**
```bash
source /opt/ros/jazzy/setup.bash
```

2. **Make it permanent:**
```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

3. **Verify installation:**
```bash
ros2 --version
# Should show: ros2 cli version X.X.X
```

---

### **Issue: "Package 'ros-jazzy-XXX' has no installation candidate"**

**Symptoms:**
```bash
$ sudo apt install ros-jazzy-navigation2
E: Unable to locate package ros-jazzy-navigation2
```

**Solutions:**

1. **Update package lists:**
```bash
sudo apt update
```

2. **Check if universe repository is enabled:**
```bash
sudo add-apt-repository universe
sudo apt update
```

3. **Verify ROS2 repository:**
```bash
sudo apt update && sudo apt install curl
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update
```

---

## 🏗️ Build Issues

### **Issue: "Package 'XXX' not found"**

**Symptoms:**
```bash
$ colcon build
Starting >>> my_package
--- stderr: my_package
CMake Error: Could not find package configuration file
```

**Solutions:**

1. **Source your workspace:**
```bash
cd ~/robot_ws
source install/setup.bash
```

2. **Install dependencies:**
```bash
rosdep install --from-paths src --ignore-src -r -y
```

3. **Check package.xml dependencies:**
```xml
<depend>missing_package_name</depend>
```

---

### **Issue: "Setup.py install is deprecated"**

**Symptoms:**
```
SetuptoolsDeprecationWarning: setup.py install is deprecated.
```

**Solution:**

Update your `setup.py`:
```python
from setuptools import setup
from glob import glob
import os

package_name = 'your_package'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your_email',
    description='Description',
    license='License',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'node_name = package_name.script_name:main'
        ],
    },
)
```

---

## 🤖 Runtime Issues

### **Issue: "No executable found"**

**Symptoms:**
```bash
$ ros2 run my_package my_node
No executable found
```

**Solutions:**

1. **Check setup.py entry_points:**
```python
entry_points={
    'console_scripts': [
        'my_node = my_package.my_node:main'  # Correct path!
    ],
},
```

2. **Rebuild package:**
```bash
cd ~/robot_ws
colcon build --packages-select my_package
source install/setup.bash
```

3. **Make Python script executable:**
```bash
chmod +x ~/robot_ws/src/my_package/my_package/my_node.py
```

4. **Check shebang line:**
```python
#!/usr/bin/env python3  # First line of .py file
```

---

### **Issue: "Node does not exist"**

**Symptoms:**
```bash
$ ros2 run my_package my_node
[ERROR] [launch]: Caught exception in launch: executable 'my_node' not found
```

**Solutions:**

1. **List available executables:**
```bash
ros2 pkg executables my_package
```

2. **Verify package installation:**
```bash
ros2 pkg list | grep my_package
```

3. **Check install directory:**
```bash
ls ~/robot_ws/install/my_package/lib/my_package/
```

---

## 📡 Communication Issues

### **Issue: "No topic '/XXX' available"**

**Symptoms:**
```bash
$ ros2 topic echo /scan
WARNING: topic [/scan] does not appear to be published yet
```

**Solutions:**

1. **List active topics:**
```bash
ros2 topic list
```

2. **Check if node is running:**
```bash
ros2 node list
```

3. **Verify topic name:**
```bash
ros2 topic info /scan
```

4. **Check QoS settings:**
```python
# Publisher
self.publisher_ = self.create_publisher(
    LaserScan, 
    'scan',
    qos_profile=qos_profile_sensor_data  # Match subscriber QoS!
)

# Subscriber  
self.subscription = self.create_subscription(
    LaserScan,
    'scan',
    self.callback,
    qos_profile=qos_profile_sensor_data  # Same QoS!
)
```

---

### **Issue: "Waiting for service to become available..."**

**Symptoms:**
```bash
Waiting for service /my_service to become available...
```

**Solutions:**

1. **Check if service exists:**
```bash
ros2 service list
```

2. **Verify service node is running:**
```bash
ros2 node list
```

3. **Check service type:**
```bash
ros2 service type /my_service
```

4. **Add timeout in client:**
```python
if not client.wait_for_service(timeout_sec=10.0):
    self.get_logger().error('Service not available!')
    return
```

---

## 🗺️ SLAM Issues

### **Issue: "Map is all gray/unknown"**

**Symptoms:**
- RViz shows completely gray map
- No obstacles visible

**Solutions:**

1. **Check LiDAR data:**
```bash
ros2 topic echo /scan --once
```

2. **Verify transforms:**
```bash
ros2 run tf2_tools view_frames
# Check if base_link -> laser_link exists
```

3. **Increase update rates:**
```yaml
# slam_params.yaml
minimum_travel_distance: 0.1  # Reduce
minimum_travel_heading: 0.1  # Reduce
```

4. **Check scan topic:**
```bash
ros2 topic hz /scan  # Should be ~10-40 Hz
```

---

### **Issue: "Robot position drifting in map"**

**Symptoms:**
- Robot appears to "slide" on map
- Map alignment poor

**Solutions:**

1. **Improve odometry:**
```python
# Check wheel separation and radius are correct
self.wheel_separation = 0.30  # Measure actual distance!
self.wheel_radius = 0.065  # Measure actual radius!
```

2. **Tune SLAM parameters:**
```yaml
# slam_params.yaml
minimum_travel_distance: 0.2
minimum_travel_heading: 0.2
scan_buffer_size: 10
scan_buffer_maximum_scan_distance: 20.0
```

3. **Calibrate IMU (if using):**
```bash
# Collect calibration data
ros2 topic echo /imu/data > imu_calibration.txt
```

---

## 🧭 Navigation Issues

### **Issue: "Failed to find a valid plan"**

**Symptoms:**
```
[planner_server]: Failed to find a valid plan!
```

**Solutions:**

1. **Check if goal is reachable:**
- Is goal in obstacle?
- Is goal too close to wall?
- Is path blocked?

2. **Adjust planner tolerance:**
```yaml
# nav2_params.yaml
planner_server:
  ros__parameters:
    tolerance: 0.5  # Increase from 0.2
```

3. **Tune costmap inflation:**
```yaml
inflation_layer:
  inflation_radius: 0.5  # Reduce if too conservative
  cost_scaling_factor: 3.0
```

4. **Check costmap:**
```bash
# Visualize in RViz
# Add -> By Topic -> /local_costmap/costmap
```

---

### **Issue: "Controller failed to make progress"**

**Symptoms:**
```
[controller_server]: Controller failed to make progress
```

**Solutions:**

1. **Increase velocity limits:**
```yaml
# nav2_params.yaml
FollowPath:
  max_vel_x: 0.5  # Increase
  max_vel_theta: 1.0  # Increase
```

2. **Reduce path lookahead:**
```yaml
lookahead_dist: 0.3  # Reduce from 0.5
```

3. **Check robot footprint:**
```yaml
robot_radius: 0.2  # Should match actual robot
# OR
footprint: "[[0.2, 0.15], [0.2, -0.15], [-0.2, -0.15], [-0.2, 0.15]]"
```

---

## 📊 Visualization Issues

### **Issue: "RViz shows 'No transform from X to Y'"**

**Symptoms:**
```
Transform [sender=unknown_publisher] For frame [laser]: No transform from [laser] to [map]
```

**Solutions:**

1. **Check TF tree:**
```bash
ros2 run tf2_tools view_frames
evince frames.pdf  # Or xdg-open frames.pdf
```

2. **Verify TF publishers:**
```bash
ros2 topic echo /tf --once
ros2 topic echo /tf_static --once
```

3. **Set correct Fixed Frame in RViz:**
- Global Options -> Fixed Frame -> "map" or "odom"

4. **Publish missing transforms:**
```python
# Static transform
from geometry_msgs.msg import TransformStamped
import tf2_ros

broadcaster = tf2_ros.StaticTransformBroadcaster(self)
t = TransformStamped()
t.header.stamp = self.get_clock().now().to_msg()
t.header.frame_id = 'base_link'
t.child_frame_id = 'laser'
t.transform.translation.x = 0.1
t.transform.rotation.w = 1.0
broadcaster.sendTransform(t)
```

---

### **Issue: "Gazebo is extremely slow"**

**Symptoms:**
- Gazebo runs at <1 FPS
- Physics update rate low

**Solutions:**

1. **Reduce rendering quality:**
   - Edit -> Camera -> Projection Type -> Orthographic

2. **Disable shadows:**
   - Right-click world -> Scene -> Disable shadows

3. **Use headless mode:**
```bash
# Launch without GUI
gzserver only
```

4. **Reduce sensor rates:**
```xml
<!-- In URDF -->
<update_rate>10</update_rate>  <!-- Reduce from 40 -->
```

5. **Use simpler physics:**
```xml
<physics type='ode'>
  <max_step_size>0.01</max_step_size>  <!-- Increase -->
  <real_time_update_rate>100</real_time_update_rate>  <!-- Reduce -->
</physics>
```

---

## 🔌 Hardware Issues

### **Issue: "Cannot open serial port /dev/ttyUSB0"**

**Symptoms:**
```
Serial error: could not open port /dev/ttyUSB0: Permission denied
```

**Solutions:**

1. **Add user to dialout group:**
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

2. **Check device exists:**
```bash
ls -l /dev/ttyUSB*
```

3. **Try different port:**
```bash
ls /dev/tty*  # Find correct port
# Often: /dev/ttyACM0 for Arduino
```

4. **Check USB cable:**
- Ensure it's a data cable, not just power

---

### **Issue: "LiDAR not publishing data"**

**Symptoms:**
```bash
$ ros2 topic hz /scan
WARNING: no messages received
```

**Solutions:**

1. **Check LiDAR power:**
- Verify LED is spinning
- Check voltage (5V for RPLIDAR)

2. **Verify driver is running:**
```bash
ros2 run rplidar_ros rplidar_composition
```

3. **Check permissions:**
```bash
sudo chmod 666 /dev/ttyUSB0
```

4. **Test with official tool:**
```bash
# RPLIDAR has test utilities
cd ~/rplidar_sdk
./ultra_simple
```

---

## 🐍 Python Issues

### **Issue: "ModuleNotFoundError: No module named 'XXX'"**

**Symptoms:**
```python
ModuleNotFoundError: No module named 'rclpy'
```

**Solutions:**

1. **Install missing Python package:**
```bash
pip3 install rclpy  # For ROS2 packages
# OR
sudo apt install python3-XXX  # For system packages
```

2. **Check PYTHONPATH:**
```bash
echo $PYTHONPATH
# Should include /opt/ros/jazzy/lib/python3.XX/site-packages
```

3. **Use rosdep:**
```bash
cd ~/robot_ws
rosdep install --from-paths src --ignore-src -r -y
```

---

## ⚙️ C++ Issues

### **Issue: "undefined reference to `XXX'"**

**Symptoms:**
```
undefined reference to `rclcpp::Node::Node(...)'
```

**Solutions:**

1. **Add library to CMakeLists.txt:**
```cmake
find_package(rclcpp REQUIRED)
ament_target_dependencies(my_node
  rclcpp
  # other dependencies
)
```

2. **Add to package.xml:**
```xml
<depend>rclcpp</depend>
```

3. **Rebuild:**
```bash
colcon build --packages-select my_package --cmake-clean-cache
```

---

## 📋 General Debugging Tips

### **1. Check Logs**
```bash
# View node output
ros2 run my_package my_node

# More verbose
ros2 run my_package my_node --ros-args --log-level debug
```

### **2. Use RQT Tools**
```bash
rqt_graph  # Visualize node connections
rqt_console  # View all logs
rqt_plot  # Plot numeric data
```

### **3. Verify Environment**
```bash
printenv | grep ROS  # Check ROS environment variables
ros2 wtf  # ROS2 diagnostic tool
```

### **4. Clean Build**
```bash
cd ~/robot_ws
rm -rf build install log
colcon build
```

### **5. Check System Resources**
```bash
htop  # CPU/Memory usage
nvidia-smi  # GPU usage (if applicable)
df -h  # Disk space
```

---

## 🆘 Still Stuck?

### **Before asking for help, collect this info:**

```bash
# 1. ROS2 version
ros2 --version

# 2. Ubuntu version
lsb_release -a

# 3. Package info
ros2 pkg list | grep my_package

# 4. Error messages (full output)
ros2 run my_package my_node 2>&1 | tee error.log

# 5. Topic/node info
ros2 node list
ros2 topic list
```

### **Where to ask:**

1. **ROS Answers**: https://answers.ros.org/
2. **ROS Discourse**: https://discourse.ros.org/
3. **Stack Overflow**: Tag with `ros2`
4. **GitHub Issues**: For code-specific problems

### **Include in your question:**

- What you're trying to do
- What you expected
- What actually happened
- Full error messages
- System info (from above)
- What you've already tried

---

## 📚 Additional Resources

- [ROS2 Troubleshooting Guide](https://docs.ros.org/en/jazzy/How-To-Guides/Troubleshooting.html)
- [Common ROS2 Errors](https://discourse.ros.org/c/general/7)
- [Nav2 Troubleshooting](https://docs.nav2.org/troubleshooting/index.html)

---

**Happy debugging! Remember: Every error is a learning opportunity! 🔧✨**
