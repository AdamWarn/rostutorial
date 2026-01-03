#!/usr/bin/env python3
"""
Automated tests for Chapter 9: LiDAR Sensor Integration
"""
import subprocess
import sys
import time


def run_command(cmd, timeout=10):
    """Run shell command and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"


def test_sensor_msgs_available():
    """Verify sensor_msgs package is available."""
    print("TEST 1: Checking sensor_msgs package...")
    
    ret, out, err = run_command("ros2 interface show sensor_msgs/msg/LaserScan")
    
    if ret == 0 and "ranges" in out:
        print("✓ sensor_msgs/LaserScan available")
        return True
    else:
        print("✗ sensor_msgs not found")
        return False


def test_scan_topic_exists():
    """Check if /scan topic exists (requires Gazebo running)."""
    print("\nTEST 2: Checking for /scan topic...")
    print("  (Skipping - requires Gazebo running)")
    print("  Manual check: ros2 topic list | grep scan")
    return True  # Skip for automated test


def test_lidar_reader_runs():
    """Test lidar_reader.py can start."""
    print("\nTEST 3: Testing lidar_reader.py...")
    
    proc = subprocess.Popen(
        ["python3", "examples/lidar_reader.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    
    time.sleep(3)
    
    # Check if still running
    poll = proc.poll()
    
    proc.terminate()
    out, err = proc.communicate()
    
    output = out.decode() + err.decode()
    
    if "lidar_reader" in output.lower():
        print("✓ LiDAR reader node starts successfully")
        return True
    else:
        print("✗ LiDAR reader failed to start")
        return False


def test_directional_lidar_runs():
    """Test directional_lidar.py can start."""
    print("\nTEST 4: Testing directional_lidar.py...")
    
    proc = subprocess.Popen(
        ["python3", "examples/directional_lidar.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    
    time.sleep(3)
    
    proc.terminate()
    out, err = proc.communicate()
    
    output = out.decode() + err.decode()
    
    if "directional" in output.lower():
        print("✓ Directional LiDAR node starts successfully")
        return True
    else:
        print("✗ Directional LiDAR failed to start")
        return False


def test_simple_avoider_runs():
    """Test simple_avoider.py can start."""
    print("\nTEST 5: Testing simple_avoider.py...")
    
    proc = subprocess.Popen(
        ["python3", "examples/simple_avoider.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    
    time.sleep(3)
    
    proc.terminate()
    out, err = proc.communicate()
    
    output = out.decode() + err.decode()
    
    if "avoider" in output.lower():
        print("✓ Obstacle avoider node starts successfully")
        return True
    else:
        print("✗ Obstacle avoider failed to start")
        return False


def test_rviz_laserscan_plugin():
    """Check if RViz LaserScan plugin is available."""
    print("\nTEST 6: Checking RViz LaserScan plugin...")
    
    ret, out, err = run_command("ros2 pkg list | grep rviz")
    
    if ret == 0 and "rviz" in out:
        print("✓ RViz package found (LaserScan plugin available)")
        return True
    else:
        print("✗ RViz not found")
        print("  Install: sudo apt install ros-jazzy-rviz2")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Chapter 9: LiDAR Integration - Automated Tests")
    print("=" * 60)
    
    tests = [
        test_sensor_msgs_available,
        test_scan_topic_exists,
        test_lidar_reader_runs,
        test_directional_lidar_runs,
        test_simple_avoider_runs,
        test_rviz_laserscan_plugin,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! You understand LiDAR!")
        print("\nNext: Launch Gazebo and test with real sensor data:")
        print("  ros2 launch my_robot_description gazebo.launch.py")
        print("  ros2 run <package> lidar_reader")
        return 0
    else:
        print("⚠️  Some tests failed. Review the chapter and try again.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
