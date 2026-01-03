# Chapter 11: SLAM Theory & Algorithms

**Goal**: Understand how SLAM works and prepare to implement it.

---

## 📖 What is SLAM?

**SLAM = Simultaneous Localization And Mapping**

The robot must solve two problems at once:
1. **Localization**: "Where am I?"
2. **Mapping**: "What does the world look like?"

**The Chicken-Egg Problem:**
- To build a map, you need to know where you are
- To know where you are, you need a map

SLAM solves both together!

---

## 🎯 LiDAR SLAM for Cleaning Robots

### What You Need
- **LiDAR sensor**: Measures distances (creates 2D or 3D scan)
- **Odometry**: Wheel encoders or IMU (estimates robot movement)
- **SLAM algorithm**: Combines sensor data to build map

### How It Works

```
1. Robot starts at position (0, 0)
2. LiDAR scans environment → sees walls
3. Robot moves forward → odometry says "moved 0.5m"
4. LiDAR scans again → sees walls from new position
5. Compare scans → correct odometry drift
6. Update map with new information
7. Repeat!
```

---

## 🧠 SLAM Algorithms

### 1. Particle Filter SLAM (GMapping)
- Uses many "particles" to represent possible robot positions
- Good for large environments
- Computationally intensive

### 2. Graph-Based SLAM (slam_toolbox) ⭐
- **This is what we'll use!**
- Creates a graph of robot poses
- Optimizes the entire graph when loop closures detected
- Good for indoor environments
- Real-time capable

### 3. EKF SLAM
- Extended Kalman Filter
- Good for small environments
- Assumes Gaussian noise

---

## 🗺️ Map Types

### Occupancy Grid Map
```
0 = Free space (white)
100 = Occupied (black)
-1 = Unknown (gray)
```

This is what cleaning robots use!

---

## 🔧 slam_toolbox

We'll use **slam_toolbox** - the industry standard for ROS2.

**Features:**
- 2D LiDAR SLAM
- Loop closure detection
- Map serialization (save/load maps)
- Localization mode
- Real-time performance

---

## 💻 Coming Next

In [Chapter 12](../chapter_12_implementing_slam/README.md), we'll:
- Set up slam_toolbox
- Create maps of simulated environments
- Tune SLAM parameters
- Save and load maps

**Full content coming in next update!**
