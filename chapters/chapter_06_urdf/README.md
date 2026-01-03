# Chapter 6: URDF - Describing Your Robot

**Goal**: Learn to describe a robot's physical structure using URDF (Unified Robot Description Format).

---

## 📖 What is URDF?

**URDF** is an XML format for describing a robot's:
- **Links** (rigid parts): chassis, wheels, sensors
- **Joints** (connections): how links move relative to each other
- **Visual** properties: what it looks like
- **Collision** properties: for physics simulation
- **Inertial** properties: mass, inertia

Think of it as a **blueprint** for your robot.

---

## 🤖 Building Blocks

### 1. Links (Rigid Bodies)

A link is a rigid part of the robot:

```xml
<link name="base_link">
  <!-- Visual: what you see -->
  <visual>
    <geometry>
      <box size="0.6 0.4 0.2"/>  <!-- length width height in meters -->
    </geometry>
    <material name="blue">
      <color rgba="0 0 0.8 1"/>  <!-- R G B Alpha -->
    </material>
  </visual>
  
  <!-- Collision: for physics -->
  <collision>
    <geometry>
      <box size="0.6 0.4 0.2"/>
    </geometry>
  </collision>
  
  <!-- Inertial: mass and inertia -->
  <inertial>
    <mass value="10.0"/>
    <inertia ixx="0.1" ixy="0" ixz="0" 
             iyy="0.1" iyz="0" 
             izz="0.1"/>
  </inertial>
</link>
```

### 2. Joints (Connections)

Joints connect links and define how they move:

**Fixed Joint** (no movement):
```xml
<joint name="lidar_joint" type="fixed">
  <parent link="base_link"/>
  <child link="lidar_link"/>
  <origin xyz="0 0 0.15" rpy="0 0 0"/>  <!-- x y z  roll pitch yaw -->
</joint>
```

**Continuous Joint** (rotates forever, like a wheel):
```xml
<joint name="left_wheel_joint" type="continuous">
  <parent link="base_link"/>
  <child link="left_wheel"/>
  <origin xyz="0 0.2 -0.05" rpy="-1.5708 0 0"/>  <!-- 90° rotation -->
  <axis xyz="0 0 1"/>  <!-- rotation axis -->
</joint>
```

**Joint Types**:
- `fixed`: No movement
- `continuous`: Rotates infinitely (wheels)
- `revolute`: Rotates with limits (robot arm)
- `prismatic`: Slides (elevator)

---

## 🚗 Example: Simple Differential Drive Robot

Let's build a simple 2-wheeled robot with a caster wheel and LiDAR!

**File**: `~/ros2_ws/src/my_robot_description/urdf/simple_robot.urdf`

```xml
<?xml version="1.0"?>
<robot name="simple_robot">
  
  <!-- Base Link (robot body) -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.6 0.4 0.2"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 0.8 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.6 0.4 0.2"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="10.0"/>
      <inertia ixx="0.2" ixy="0" ixz="0" 
               iyy="0.3" iyz="0" 
               izz="0.4"/>
    </inertial>
  </link>
  
  <!-- Left Wheel -->
  <link name="left_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black">
        <color rgba="0 0 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.001" ixy="0" ixz="0" 
               iyy="0.001" iyz="0" 
               izz="0.001"/>
    </inertial>
  </link>
  
  <joint name="left_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="left_wheel"/>
    <origin xyz="0 0.225 -0.05" rpy="-1.5708 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>
  
  <!-- Right Wheel -->
  <link name="right_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black">
        <color rgba="0 0 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.001" ixy="0" ixz="0" 
               iyy="0.001" iyz="0" 
               izz="0.001"/>
    </inertial>
  </link>
  
  <joint name="right_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="right_wheel"/>
    <origin xyz="0 -0.225 -0.05" rpy="-1.5708 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>
  
  <!-- Caster Wheel (simplified as sphere) -->
  <link name="caster_wheel">
    <visual>
      <geometry>
        <sphere radius="0.05"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <sphere radius="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.2"/>
      <inertia ixx="0.0001" ixy="0" ixz="0" 
               iyy="0.0001" iyz="0" 
               izz="0.0001"/>
    </inertial>
  </link>
  
  <joint name="caster_joint" type="fixed">
    <parent link="base_link"/>
    <child link="caster_wheel"/>
    <origin xyz="-0.25 0 -0.15" rpy="0 0 0"/>
  </joint>
  
  <!-- LiDAR Sensor -->
  <link name="lidar_link">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.04"/>
      </geometry>
      <material name="red">
        <color rgba="0.8 0 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.05" length="0.04"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.1"/>
      <inertia ixx="0.00001" ixy="0" ixz="0" 
               iyy="0.00001" iyz="0" 
               izz="0.00001"/>
    </inertial>
  </link>
  
  <joint name="lidar_joint" type="fixed">
    <parent link="base_link"/>
    <child link="lidar_link"/>
    <origin xyz="0.2 0 0.15" rpy="0 0 0"/>
  </joint>
  
</robot>
```

---

## 👁️ Visualizing Your Robot

### Step 1: Create Package

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python my_robot_description
```

### Step 2: Create URDF Directory

```bash
mkdir -p ~/ros2_ws/src/my_robot_description/urdf
```

### Step 3: Copy the URDF

Save the XML above to: `~/ros2_ws/src/my_robot_description/urdf/simple_robot.urdf`

### Step 4: Install URDF Files

Edit `setup.py`:

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

### Step 5: Build

```bash
cd ~/ros2_ws
colcon build --packages-select my_robot_description
source install/setup.bash
```

### Step 6: View in RViz

```bash
# Install joint-state-publisher GUI
sudo apt install ros-jazzy-joint-state-publisher-gui

# View the robot
ros2 run joint_state_publisher_gui joint_state_publisher_gui \
  ~/ros2_ws/src/my_robot_description/urdf/simple_robot.urdf &

# Start RViz
rviz2
```

**In RViz**:
1. Click "Add" → "RobotModel"
2. Set "Fixed Frame" to "base_link"
3. You should see your robot!

---

## 🎨 Understanding Coordinate Frames

### Origin and RYP

```xml
<origin xyz="0.2 0 0.15" rpy="0 0 1.5708"/>
```

- **xyz**: Translation (meters)
  - `x`: forward/backward
  - `y`: left/right
  - `z`: up/down

- **rpy**: Rotation (radians)
  - `r`: roll (rotation around x-axis)
  - `p`: pitch (rotation around y-axis)
  - `y`: yaw (rotation around z-axis)

**Common rotations**:
- 90° = 1.5708 radians
- 180° = 3.14159 radians
- -90° = -1.5708 radians

---

## 💻 Exercises

### Exercise 6.1: Add Front Bumper

Add a bumper sensor to the front of the robot:

```xml
<link name="front_bumper">
  <visual>
    <geometry>
      <box size="0.05 0.4 0.1"/>
    </geometry>
    <material name="yellow">
      <color rgba="1 1 0 1"/>
    </material>
  </visual>
</link>

<joint name="bumper_joint" type="fixed">
  <parent link="base_link"/>
  <child link="front_bumper"/>
  <origin xyz="0.325 0 -0.05" rpy="0 0 0"/>
</joint>
```

### Exercise 6.2: Create Your Own Robot

Design a robot with:
- A different chassis shape (cylinder, custom dimensions)
- 4 wheels instead of 2 + caster
- Multiple sensors (camera, IMU, ultrasonic)

### Exercise 6.3: Calculate Inertia

For a box with mass `m`, length `l`, width `w`, height `h`:

```
ixx = (1/12) * m * (w² + h²)
iyy = (1/12) * m * (l² + h²)
izz = (1/12) * m * (l² + w²)
```

Calculate correct inertia for a 10kg robot: 0.6m × 0.4m × 0.2m

---

## 🔧 URDF Best Practices

1. **Always start with `base_link`** - the main body
2. **Use meters** for all measurements
3. **Use radians** for all angles
4. **Make visual = collision** for simple shapes
5. **Add inertial properties** - required for Gazebo
6. **Use descriptive names** - `left_wheel` not `link_1`
7. **Test in RViz** before Gazebo

---

## 🎯 Key Takeaways

- URDF describes robot **structure** in XML
- **Links** are rigid parts
- **Joints** connect links
- **Visual**, **Collision**, **Inertial** properties
- **RViz** visualizes URDF
- **Gazebo** will simulate physics (next chapter!)

---

## 🚀 Next Chapter

[Chapter 7: Gazebo Simulation](../chapter_07_gazebo/README.md) - Bring your robot to life in a 3D physics simulator!

---

## 📚 Additional Resources

- [URDF Tutorials](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/URDF/URDF-Main.html)
- [URDF XML Specification](http://wiki.ros.org/urdf/XML)
- [Inertia Calculator](https://en.wikipedia.org/wiki/List_of_moments_of_inertia)
