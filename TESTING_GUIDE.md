# 🧪 Testing Guide

**How to run and verify the ROS2 SLAM Robot course tests**

---

## 🚀 Quick Start

### Run All Tests

```bash
cd ~/rostutorial
python3 run_tests.py
```

### Run Specific Chapter

```bash
# Test only Chapter 3
python3 run_tests.py 3

# Test multiple chapters
python3 run_tests.py 1 3 5 8
```

### Verbose Output

```bash
# See detailed test output
python3 run_tests.py --verbose

# Verbose for specific chapter
python3 run_tests.py 3 --verbose
```

---

## 📋 What Gets Tested

### **Automated Tests Available:**

| Chapter | Test Coverage | Status |
|---------|--------------|--------|
| Chapter 1 | ROS2 installation, workspace setup | ✅ Complete |
| Chapter 2 | Core concepts, turtlesim | ✅ Complete |
| Chapter 3 | Python nodes, pub/sub | ✅ Complete |
| Chapter 4 | C++ nodes, compilation | ✅ Complete |
| Chapter 5 | Launch files, parameters | ✅ Complete |
| Chapter 6 | URDF validation | ✅ Complete |
| Chapter 7 | Gazebo simulation | ✅ Complete |
| Chapter 8 | TF2 transforms | ✅ Complete |
| Chapter 9 | LiDAR integration | ✅ Complete |
| Chapter 10 | Custom messages | ✅ Complete |
| Chapter 11+ | Advanced topics | 📝 Manual verification |

---

## 🎯 Test Types

### **1. Environment Tests**

Verify your system is set up correctly:
- ROS2 Jazzy installed
- Required packages available
- Workspace structure correct

**Example:**
```bash
python3 chapters/chapter_01_introduction/tests/test_chapter_01.py
```

---

### **2. Build Tests**

Check that packages compile:
- Python package structure
- C++ compilation
- Dependencies resolved

**Example:**
```bash
python3 chapters/chapter_04_cpp_pubsub/tests/test_chapter_04.py
```

---

### **3. Runtime Tests**

Verify nodes run correctly:
- Nodes start without errors
- Topics publish/subscribe
- Services respond
- Transforms broadcast

**Example:**
```bash
python3 chapters/chapter_08_tf2/tests/test_chapter_08.py
```

---

## 🔍 Understanding Test Output

### **Success:**

```
══════════════════════════════════════════════════════════════════
  ROS2 SLAM Robot Course - Automated Test Suite
══════════════════════════════════════════════════════════════════

──────────────────────────────────────────────────────────────────
Running Chapter 1: chapter_01_introduction
──────────────────────────────────────────────────────────────────

[TEST] ROS2 Installation
  ✓ ROS2 Jazzy is installed
  ✓ Version: ros2 cli version 0.32.1
  
PASSED in 2.34s

══════════════════════════════════════════════════════════════════
Test Summary:

  ✓ PASS - Chapter 1: chapter_01_introduction
  
Results:
  Passed: 1
  Failed: 0
  Total:  1

Success Rate: 100.0%
══════════════════════════════════════════════════════════════════
```

---

### **Failure:**

```
[TEST] Build Workspace
  ✗ colcon build failed
  ⚠ Error: package 'my_package' not found

FAILED in 15.21s

══════════════════════════════════════════════════════════════════
Test Summary:

  ✗ FAIL - Chapter 3: chapter_03_python_pubsub
    Run with --verbose for details
  
Results:
  Passed: 0
  Failed: 1
  Total:  1

Success Rate: 0.0%
══════════════════════════════════════════════════════════════════
```

---

## 🐛 Troubleshooting Failed Tests

### **"ROS2 not found"**

**Problem:** ROS2 environment not sourced

**Solution:**
```bash
source /opt/ros/jazzy/setup.bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
```

---

### **"Package not found during build"**

**Problem:** Missing dependencies

**Solution:**
```bash
cd ~/robot_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build
```

---

### **"Node fails to start"**

**Problem:** Script not executable or missing shebang

**Solution:**
```bash
chmod +x your_node.py
# Ensure first line is: #!/usr/bin/env python3
```

---

### **"Test timeout"**

**Problem:** Test waiting for node that never starts

**Solution:**
```bash
# Check if node runs manually
ros2 run my_package my_node

# Check for errors
ros2 run my_package my_node --ros-args --log-level debug
```

---

## 📝 Manual Testing

For chapters without automated tests, verify manually:

### **Chapter 12: SLAM**

```bash
# Terminal 1: Launch simulation
ros2 launch robot_bringup simulation.launch.py

# Terminal 2: Start SLAM
ros2 launch slam_toolbox online_async_launch.py

# Terminal 3: Visualize
rviz2

# Verify: Map appears in RViz as robot moves
```

---

### **Chapter 15: Navigation**

```bash
# Launch full navigation stack
ros2 launch robot_bringup navigation.launch.py

# Send goal in RViz
# Click "2D Goal Pose" and place on map

# Verify: Robot navigates to goal
```

---

## ✅ Verification Checklist

Before moving to next chapter, ensure:

- [ ] All automated tests pass
- [ ] Code examples run without errors
- [ ] Can explain key concepts
- [ ] Completed at least 50% of exercises
- [ ] No unresolved error messages

---

## 🎯 Test-Driven Learning

**Use tests to guide your learning:**

1. **Before starting chapter:**
   ```bash
   python3 run_tests.py <chapter_num>
   # Should fail - you haven't done it yet!
   ```

2. **Work through chapter:**
   - Read material
   - Run examples
   - Complete exercises

3. **After completing chapter:**
   ```bash
   python3 run_tests.py <chapter_num>
   # Should pass - you did it!
   ```

4. **Regression testing:**
   ```bash
   python3 run_tests.py  # All previous chapters should still pass
   ```

---

## 🔧 Writing Your Own Tests

### **Test Template:**

```python
#!/usr/bin/env python3
"""
Chapter X Test Suite
"""

import subprocess
import sys

def run_command(cmd):
    """Run command and return success"""
    result = subprocess.run(
        cmd, 
        shell=True, 
        capture_output=True, 
        text=True,
        timeout=10
    )
    return result.returncode == 0

def test_my_feature():
    """Test specific feature"""
    print("[TEST] My Feature")
    
    success = run_command("ros2 run my_package my_node --help")
    
    if success:
        print("  ✓ Feature works")
        return True
    else:
        print("  ✗ Feature failed")
        return False

def main():
    passed = test_my_feature()
    sys.exit(0 if passed else 1)

if __name__ == '__main__':
    main()
```

---

## 📊 Continuous Testing

### **During Development:**

```bash
# Watch mode - rerun tests on file changes
# (requires 'entr' package)
ls chapters/chapter_03_python_pubsub/**/*.py | entr python3 run_tests.py 3
```

### **Before Committing Code:**

```bash
# Always run full test suite
python3 run_tests.py

# Only commit if all tests pass
git commit -m "Your message"
```

---

## 🎓 Learning from Test Failures

**Failed tests are learning opportunities!**

When a test fails:

1. **Read error message carefully**
   - What was expected?
   - What actually happened?

2. **Run with verbose mode**
   ```bash
   python3 run_tests.py <chapter> --verbose
   ```

3. **Test components individually**
   ```bash
   ros2 run my_package my_node  # Does node start?
   ros2 topic list  # Are topics created?
   ```

4. **Check logs**
   ```bash
   ros2 run my_package my_node --ros-args --log-level debug
   ```

5. **Compare with working example**
   - Check chapter's example code
   - Look for differences

---

## 📚 Additional Resources

- **Troubleshooting Guide**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **ROS2 Testing Docs**: https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Testing/Testing-Main.html
- **Python unittest**: https://docs.python.org/3/library/unittest.html

---

## 💡 Pro Tips

1. **Test early, test often** - Don't wait until chapter end
2. **Fix failures immediately** - Don't accumulate technical debt
3. **Keep notes** - Document what fixes worked
4. **Ask for help** - Use ROS Discourse if stuck
5. **Celebrate passes** - You're making progress! 🎉

---

**Happy Testing! Every green checkmark is progress! ✅**
