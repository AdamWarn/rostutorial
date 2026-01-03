# Chapter 14: Nav2 Stack Overview

**Goal**: Understand the Navigation2 stack architecture.

---

## 📖 What is Nav2?

**Navigation2 (Nav2)** is the ROS2 navigation system. It takes a map and goal, then:
1. Plans a path
2. Follows the path
3. Avoids obstacles
4. Reaches the goal

Perfect for cleaning robots!

---

## 🏗️ Nav2 Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Nav2 Stack                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐          ┌──────────────┐       │
│  │ Global       │          │  Local       │       │
│  │ Planner      │─────────▶│  Planner     │       │
│  │ (Path)       │          │  (Trajectory)│       │
│  └──────────────┘          └──────────────┘       │
│         │                         │                │
│         ▼                         ▼                │
│  ┌──────────────────────────────────────────┐     │
│  │         Controller Server                │     │
│  │   (Follows path, sends velocity)         │     │
│  └──────────────────────────────────────────┘     │
│         │                                          │
│         ▼                                          │
│  ┌──────────────┐    ┌──────────────┐            │
│  │  Costmap     │    │  Recovery    │            │
│  │  (Obstacles) │    │  Behaviors   │            │
│  └──────────────┘    └──────────────┘            │
└─────────────────────────────────────────────────────┘
         │
         ▼
  ┌──────────────┐
  │ /cmd_vel     │  → To robot motors
  └──────────────┘
```

---

## 🎯 Key Components

### 1. **Planner Server**
- Plans global path from start to goal
- Uses map
- Algorithms: NavFn, Smac Planner

### 2. **Controller Server**
- Follows the planned path
- Generates velocity commands
- Algorithms: DWB, TEB, RPP

### 3. **Costmap**
- Represents obstacles
- Global costmap: Full map
- Local costmap: Around robot

### 4. **Recovery Behaviors**
- What to do when stuck
- Spin, backup, wait, etc.

### 5. **Behavior Tree**
- Coordinates everything
- Handles logic flow

---

## 🚀 How It Works

```
1. You send a goal: "Go to (5, 10)"
2. Planner creates path
3. Controller follows path
4. Costmap updated with obstacles
5. Controller avoids obstacles
6. If stuck → Recovery behavior
7. Reaches goal!
```

---

## 💻 Coming Soon

In [Chapter 15](../chapter_15_path_planning/README.md), we'll configure Nav2 for your robot!

**Full implementation coming in next update!**
