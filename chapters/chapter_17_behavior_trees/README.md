# Chapter 17: Behavior Trees for Robot Control

**Goal**: Learn to coordinate complex robot behaviors using Behavior Trees!

---

## 📖 What are Behavior Trees?

**Behavior Trees (BT)** organize robot actions like a decision flowchart.

### Understanding with a Real Example

Think about **making breakfast**:

```
Make Breakfast
├─ Sequence (do these in order)
│  ├─ Check if hungry
│  ├─ Go to kitchen
│  ├─ Parallel (do at same time)
│  │  ├─ Make toast
│  │  └─ Brew coffee
│  └─ Eat
```

**If NOT hungry** → Skip everything
**If hungry** → Do each step in order

---

## 🌳 Basic Concepts

### What is a Tree?

A **tree** in programming is a hierarchical structure:

```
         Root
        /    \
    Branch  Branch
    /  \      |
  Leaf Leaf  Leaf
```

- **Root**: Starting point
- **Branches**: Decisions or groupings
- **Leaves**: Actual actions

---

### BT vs. State Machines

**State Machine** (old way):
```
IDLE → SEARCHING → MOVING → CLEANING → IDLE
```
- Hard to add new behaviors
- Complex connections

**Behavior Tree** (better way):
```
CleaningBehavior
├─ If battery low → Charge
├─ Else
│  ├─ Search for dirt
│  └─ Clean dirt
```
- Easy to add behaviors
- Clear hierarchy

---

## 🎯 BT Node Types

### 1. Action Nodes (Do Something)

**Actions** are the actual tasks:

```python
class MoveForward(ActionNode):
    """Drive forward for a distance."""
    
    def execute(self):
        # Code to move robot
        self.robot.move(speed=0.3, distance=1.0)
        return SUCCESS  # or FAILURE
```

---

### 2. Condition Nodes (Check Something)

**Conditions** ask yes/no questions:

```python
class IsBatteryLow(ConditionNode):
    """Check if battery needs charging."""
    
    def check(self):
        if self.robot.battery < 20:
            return True  # Yes, battery is low
        else:
            return False  # No, battery is fine
```

---

### 3. Sequence Nodes (Do All in Order)

**Sequence**: Do children one by one. If ANY fails, stop.

```
Sequence
├─ Open door       ← Do this first
├─ Walk through    ← Then this
└─ Close door      ← Finally this

If "Open door" fails → Don't try the rest
```

```python
sequence = Sequence("Enter Room", children=[
    OpenDoor(),
    WalkThrough(),
    CloseDoor()
])
```

---

### 4. Fallback/Selector Nodes (Try Until Success)

**Fallback**: Try children until ONE succeeds.

```
Fallback (try these in order)
├─ Find charging dock  ← Try first
├─ Navigate to dock    ← If found, try this
└─ Emergency stop      ← If navigation fails, do this
```

```python
fallback = Fallback("Get Charged", children=[
    FindChargingDock(),
    NavigateToDock(),
    EmergencyStop()
])
```

---

### 5. Parallel Nodes (Do Multiple at Once)

**Parallel**: Run multiple children simultaneously.

```
Parallel
├─ Monitor battery    ← Keep checking
├─ Scan for obstacles ← While also scanning
└─ Navigate to goal   ← While moving
```

---

## 🤖 Simple Cleaning Robot BT

### Plain English Logic

```
Main Behavior:
1. Is battery low?
   → Yes: Go charge
   → No: Continue
2. Search for dirty area
3. Navigate to dirty area
4. Clean the area
5. Repeat
```

---

### As a Behavior Tree

```xml
<BehaviorTree>
  <Sequence name="CleaningLoop">
    
    <!-- Check battery first -->
    <Fallback>
      <Inverter>  <!-- Inverter flips result -->
        <Condition name="IsBatteryLow"/>
      </Inverter>
      <Action name="GoToChargingStation"/>
    </Fallback>
    
    <!-- Main cleaning sequence -->
    <Sequence>
      <Action name="SearchForDirt"/>
      <Action name="NavigateToDirt"/>
      <Action name="CleanArea"/>
    </Sequence>
    
  </Sequence>
</BehaviorTree>
```

---

## 💻 Using Nav2 Behavior Trees

Nav2 uses **BehaviorTree.CPP** library.

### Installing BT Tools

```bash
# Install Nav2 BT tools
sudo apt install ros-jazzy-nav2-bt-navigator

# Install BT visualization tool
sudo apt install ros-jazzy-behaviortree-cpp-v3
```

---

### Nav2's Default BT

Nav2 includes a default navigation BT at:
```
/opt/ros/jazzy/share/nav2_bt_navigator/behavior_trees/navigate_w_replanning.xml
```

**What it does**:
1. Compute path to goal
2. Follow path
3. If obstacle appears → Replan
4. If stuck → Execute recovery behaviors
5. Retry

---

## 🛠️ Creating Custom BT in Python

### Simple Action Node

```python
import py_trees
from py_trees.common import Status

class CheckBattery(py_trees.behaviour.Behaviour):
    """
    Behavior to check if battery is low.
    
    Returns:
      SUCCESS if battery is OK
      FAILURE if battery is low
    """
    
    def __init__(self, name, battery_threshold=20.0):
        super().__init__(name)
        self.battery_threshold = battery_threshold
    
    def update(self):
        """
        This function runs when the BT "ticks" this node.
        
        Think of "tick" like asking "what's your status?"
        """
        # Get battery level (simplified)
        battery_level = self.get_battery_level()
        
        if battery_level < self.battery_threshold:
            self.feedback_message = f"Battery low: {battery_level}%"
            return Status.FAILURE  # Battery is low!
        else:
            self.feedback_message = f"Battery OK: {battery_level}%"
            return Status.SUCCESS  # Battery is fine
    
    def get_battery_level(self):
        """Get current battery percentage."""
        # In real robot, read from battery topic
        # For now, return dummy value
        return 75.0
```

---

### Action to Navigate

```python
class NavigateToGoal(py_trees.behaviour.Behaviour):
    """Send navigation goal to Nav2."""
    
    def __init__(self, name, x, y):
        super().__init__(name)
        self.goal_x = x
        self.goal_y = y
        self.nav_client = None  # Action client for Nav2
    
    def setup(self):
        """Called once when BT starts."""
        # Create Nav2 action client
        # (Simplified - needs actual ROS2 node)
        self.feedback_message = "Navigation action ready"
    
    def update(self):
        """
        Called repeatedly while this action is active.
        
        Returns:
          RUNNING - Still navigating
          SUCCESS - Reached goal
          FAILURE - Navigation failed
        """
        if not self.is_navigating():
            # Start navigation
            self.send_nav_goal(self.goal_x, self.goal_y)
            return Status.RUNNING
        
        # Check if reached goal
        if self.reached_goal():
            self.feedback_message = "Goal reached!"
            return Status.SUCCESS
        
        # Check if failed
        if self.navigation_failed():
            self.feedback_message = "Navigation failed!"
            return Status.FAILURE
        
        # Still navigating
        return Status.RUNNING
```

---

### Building the Tree

```python
import py_trees

def create_cleaning_tree():
    """
    Build a complete cleaning behavior tree.
    
    Tree structure:
      Root
      └─ Sequence
         ├─ Battery Check (fallback)
         └─ Cleaning Sequence
    """
    
    # Root node
    root = py_trees.composites.Sequence(
        name="CleaningBehavior",
        memory=True  # Remember state between ticks
    )
    
    # Battery management (fallback = try until success)
    battery_check = py_trees.composites.Selector(
        name="BatteryManagement",
        memory=False
    )
    
    # Check if battery is OK
    battery_ok = CheckBattery("BatteryOK", battery_threshold=20.0)
    
    # If battery low, charge
    go_charge = NavigateToGoal("GoCharge", x=0.0, y=0.0)  # Charging station
    
    # Add to battery check
    battery_check.add_children([battery_ok, go_charge])
    
    # Cleaning sequence
    cleaning_seq = py_trees.composites.Sequence(
        name="CleaningSequence"
    )
    
    cleaning_seq.add_children([
        NavigateToGoal("GoToRoom1", x=2.0, y=1.0),
        py_trees.behaviours.Success("CleanRoom"),  # Placeholder
        NavigateToGoal("GoToRoom2", x=4.0, y=2.0),
        py_trees.behaviours.Success("CleanRoom"),  # Placeholder
    ])
    
    # Build final tree
    root.add_children([battery_check, cleaning_seq])
    
    return root


# Create and run tree
tree = create_cleaning_tree()

# Display tree structure
py_trees.display.render_dot_tree(tree, name="cleaning_tree")

# Run tree (tick it)
tree.setup_with_descendants()
tree.tick_once()
```

---

## 📊 Visualizing Behavior Trees

### Using Groot (BT Monitor)

```bash
# Install Groot
sudo apt install ros-jazzy-groot

# Run Groot
groot
```

**In Groot**:
1. Load your BT XML file
2. See tree structure visually
3. Monitor live execution
4. Debug behavior

---

## 🎯 Common Patterns

### Pattern 1: Retry with Timeout

```xml
<Sequence>
  <RetryUntilSuccessful num_attempts="3">
    <Action name="TryAction"/>
  </RetryUntilSuccessful>
  
  <Fallback>
    <!-- If retries failed, do recovery -->
    <Action name="RecoveryAction"/>
  </Fallback>
</Sequence>
```

---

### Pattern 2: Conditional Execution

```python
# Only clean if dirt detected
cleaning_if_dirty = py_trees.composites.Sequence(
    "CleanIfDirty",
    children=[
        ConditionNode("IsDirtDetected"),  # Check condition
        ActionNode("CleanDirt")           # Only runs if condition true
    ]
)
```

---

### Pattern 3: Parallel Monitoring

```python
# Monitor safety while navigating
safe_navigation = py_trees.composites.Parallel(
    name="SafeNavigation",
    policy=py_trees.common.ParallelPolicy.SuccessOnOne()
)

safe_navigation.add_children([
    NavigateToGoal("Navigate", 5.0, 3.0),
    MonitorBattery("BatteryMonitor"),
    MonitorObstacles("ObstacleMonitor"),
])
```

---

## 💻 Exercises

### Exercise 17.1: Build Simple BT

Create a BT that:
1. Checks battery
2. If low: navigate to (0,0)
3. If OK: navigate to (2,2)

### Exercise 17.2: Patrol with Recovery

Create a BT that:
- Patrols between 3 waypoints
- If navigation fails → Spin in place → Retry
- If stuck after 3 retries → Call for help

### Exercise 17.3: Priority Behaviors

Create a BT with priorities:
1. Highest: Battery critical → Emergency charge
2. Medium: Cleaning task
3. Lowest: Return to dock

---

## 🎯 Key Takeaways

1. **Behavior Trees** organize complex behaviors hierarchically
2. **Nodes** can be Actions, Conditions, or Composites
3. **Sequence** runs children in order (all must succeed)
4. **Fallback** tries children until one succeeds
5. **Parallel** runs multiple children simultaneously
6. **Nav2 uses BT** for navigation coordination
7. **Groot** visualizes and debugs BTs

---

## 🚀 Next Chapter

[Chapter 18: Advanced Coverage Planning](../chapter_18_advanced_coverage/README.md) - Room segmentation and optimized cleaning patterns!

---

## 📚 Resources

- [BehaviorTree.CPP](https://www.behaviortree.dev/)
- [py_trees](https://py-trees.readthedocs.io/)
- [Nav2 BT Tutorial](https://docs.nav2.org/behavior_trees/index.html)
- [Groot](https://github.com/BehaviorTree/Groot)
