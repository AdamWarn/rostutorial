#!/usr/bin/env python3
"""
Automated tests for Chapter 8: TF2 Coordinate Frames & Transformations
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


def test_tf2_tools_installed():
    """Verify TF2 tools are installed."""
    print("TEST 1: Checking TF2 tools installation...")
    
    ret, out, err = run_command("ros2 pkg list | grep tf2_tools")
    
    if ret == 0 and "tf2_tools" in out:
        print("✓ tf2_tools installed")
        return True
    else:
        print("✗ tf2_tools not found. Install with:")
        print("  sudo apt install ros-jazzy-tf2-tools ros-jazzy-tf2-ros")
        return False


def test_tf_transformations_installed():
    """Verify tf_transformations is installed."""
    print("\nTEST 2: Checking tf_transformations...")
    
    ret, out, err = run_command(
        "python3 -c 'from tf_transformations import quaternion_from_euler'")
    
    if ret == 0:
        print("✓ tf_transformations installed")
        return True
    else:
        print("✗ tf_transformations not found. Install with:")
        print("  sudo apt install ros-jazzy-tf-transformations")
        return False


def test_static_frame_publisher():
    """Test static transform publisher example."""
    print("\nTEST 3: Testing static frame publisher...")
    
    # Start node in background
    proc = subprocess.Popen(
        ["python3", "examples/static_frame_publisher.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    
    time.sleep(3)
    
    # Check if TF is being published
    ret, out, err = run_command(
        "ros2 topic echo /tf_static --once", timeout=5)
    
    proc.terminate()
    proc.wait()
    
    if ret == 0 and "base_link" in out:
        print("✓ Static transform published successfully")
        return True
    else:
        print("✗ Static transform not detected")
        return False


def test_dynamic_broadcaster():
    """Test dynamic transform broadcaster."""
    print("\nTEST 4: Testing dynamic broadcaster...")
    
    # Start node in background
    proc = subprocess.Popen(
        ["python3", "examples/dynamic_frame_broadcaster.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    
    time.sleep(3)
    
    # Check if TF is being published
    ret, out, err = run_command(
        "ros2 topic echo /tf --once", timeout=5)
    
    proc.terminate()
    proc.wait()
    
    if ret == 0 and "odom" in out and "base_link" in out:
        print("✓ Dynamic transform broadcast successfully")
        return True
    else:
        print("✗ Dynamic transform not detected")
        return False


def test_frame_listener():
    """Test frame listener example."""
    print("\nTEST 5: Testing frame listener...")
    
    # Start static publisher first
    static_proc = subprocess.Popen(
        ["python3", "examples/static_frame_publisher.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    
    time.sleep(2)
    
    # Start listener
    listener_proc = subprocess.Popen(
        ["python3", "examples/frame_listener.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    
    time.sleep(3)
    
    listener_proc.terminate()
    out, err = listener_proc.communicate()
    
    static_proc.terminate()
    static_proc.wait()
    
    output = out.decode() + err.decode()
    
    if "Translation:" in output or "Transform" in output:
        print("✓ Frame listener working")
        return True
    else:
        print("✗ Frame listener failed")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Chapter 8: TF2 Coordinate Frames - Automated Tests")
    print("=" * 60)
    
    tests = [
        test_tf2_tools_installed,
        test_tf_transformations_installed,
        test_static_frame_publisher,
        test_dynamic_broadcaster,
        test_frame_listener,
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
        print("🎉 All tests passed! You understand TF2!")
        return 0
    else:
        print("⚠️  Some tests failed. Review the chapter and try again.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
