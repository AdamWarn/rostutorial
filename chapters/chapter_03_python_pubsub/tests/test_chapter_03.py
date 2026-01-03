#!/usr/bin/env python3
"""
Chapter 3 Test Suite - Python Publishers & Subscribers
Tests package creation, node functionality, and exercises
"""

import subprocess
import sys
import time
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test(name):
    print(f"\n{Colors.BLUE}[TEST]{Colors.RESET} {name}")

def print_pass(message):
    print(f"  {Colors.GREEN}✓{Colors.RESET} {message}")

def print_fail(message):
    print(f"  {Colors.RED}✗{Colors.RESET} {message}")

def print_info(message):
    print(f"  {Colors.YELLOW}ℹ{Colors.RESET} {message}")

def run_command(cmd, shell=False, timeout=15):
    """Run a command and return success, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_workspace_exists():
    """Test 1: Check if workspace exists"""
    print_test("Testing Workspace Structure")
    
    home = Path.home()
    workspace = home / "ros2_ws" / "src"
    
    if workspace.exists():
        print_pass(f"Workspace found at {workspace}")
        return True
    else:
        print_fail(f"Workspace not found at {workspace}")
        print_info("Create with: mkdir -p ~/ros2_ws/src")
        return False

def test_package_exists():
    """Test 2: Check if student created my_first_pkg"""
    print_test("Testing Package Creation")
    
    home = Path.home()
    pkg_path = home / "ros2_ws" / "src" / "my_first_pkg"
    
    if pkg_path.exists():
        print_pass("Package 'my_first_pkg' found")
        
        # Check for key files
        files_to_check = [
            "package.xml",
            "setup.py",
            "my_first_pkg/__init__.py"
        ]
        
        all_exist = True
        for file_name in files_to_check:
            file_path = pkg_path / file_name
            if file_path.exists():
                print_pass(f"  {file_name} exists")
            else:
                print_fail(f"  {file_name} missing")
                all_exist = False
        
        return all_exist
    else:
        print_fail("Package 'my_first_pkg' not found")
        print_info("Create with: ros2 pkg create --build-type ament_python my_first_pkg --dependencies rclpy std_msgs")
        return False

def test_python_files_exist():
    """Test 3: Check if Python node files exist"""
    print_test("Testing Python Node Files")
    
    home = Path.home()
    pkg_path = home / "ros2_ws" / "src" / "my_first_pkg" / "my_first_pkg"
    
    nodes = {
        "simple_publisher.py": "Publisher node",
        "simple_subscriber.py": "Subscriber node",
    }
    
    all_exist = True
    for filename, description in nodes.items():
        filepath = pkg_path / filename
        if filepath.exists():
            print_pass(f"{description} ({filename}) exists")
        else:
            print_fail(f"{description} ({filename}) missing")
            print_info(f"Create this file in ~/ros2_ws/src/my_first_pkg/my_first_pkg/")
            all_exist = False
    
    return all_exist

def test_package_builds():
    """Test 4: Check if package builds successfully"""
    print_test("Testing Package Build")
    
    home = Path.home()
    workspace = home / "ros2_ws"
    
    if not workspace.exists():
        print_fail("Workspace doesn't exist")
        return False
    
    print_info("Attempting to build my_first_pkg (this may take a moment)...")
    
    success, stdout, stderr = run_command(
        f"bash -c 'cd {workspace} && source /opt/ros/jazzy/setup.bash && colcon build --packages-select my_first_pkg'",
        shell=True,
        timeout=60
    )
    
    if success and "Finished" in stdout:
        print_pass("Package builds successfully")
        return True
    else:
        print_fail("Package build failed")
        if stderr:
            print_info(f"Error output (first 200 chars): {stderr[:200]}")
        return False

def test_entry_points():
    """Test 5: Check if entry points are configured in setup.py"""
    print_test("Testing Entry Points Configuration")
    
    home = Path.home()
    setup_py = home / "ros2_ws" / "src" / "my_first_pkg" / "setup.py"
    
    if not setup_py.exists():
        print_fail("setup.py not found")
        return False
    
    with open(setup_py, 'r') as f:
        content = f.read()
    
    required_entries = [
        'entry_points',
        'console_scripts',
        'simple_publisher',
        'simple_subscriber',
    ]
    
    all_found = True
    for entry in required_entries:
        if entry in content:
            print_pass(f"Found '{entry}' in setup.py")
        else:
            print_fail(f"Missing '{entry}' in setup.py")
            all_found = False
    
    return all_found

def test_nodes_executable():
    """Test 6: Check if nodes can be executed"""
    print_test("Testing Node Executability")
    
    home = Path.home()
    workspace = home / "ros2_ws"
    
    # Source and try to get help from the node
    test_cmd = f"bash -c 'source /opt/ros/jazzy/setup.bash && source {workspace}/install/setup.bash && ros2 pkg list | grep my_first_pkg'"
    
    success, stdout, stderr = run_command(test_cmd, shell=True)
    
    if success and "my_first_pkg" in stdout:
        print_pass("Package is discoverable by ROS2")
        return True
    else:
        print_fail("Package not found in ROS2 package list")
        print_info("Build and source: cd ~/ros2_ws && colcon build && source install/setup.bash")
        return False

def test_message_flow():
    """Test 7: Test actual message flow between nodes"""
    print_test("Testing Message Flow (Publisher -> Subscriber)")
    
    home = Path.home()
    workspace = home / "ros2_ws"
    
    print_info("Starting publisher node...")
    
    # Start publisher
    pub_cmd = f"bash -c 'source /opt/ros/jazzy/setup.bash && source {workspace}/install/setup.bash && ros2 run my_first_pkg simple_publisher'"
    
    try:
        pub_proc = subprocess.Popen(
            pub_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give it time to start
        time.sleep(3)
        
        # Check if topic exists
        topic_cmd = "bash -c 'source /opt/ros/jazzy/setup.bash && ros2 topic list'"
        success, stdout, _ = run_command(topic_cmd, shell=True)
        
        if success and "chatter" in stdout:
            print_pass("Publisher is publishing to /chatter topic")
            
            # Try to echo one message
            echo_cmd = "bash -c 'source /opt/ros/jazzy/setup.bash && timeout 3 ros2 topic echo /chatter --once'"
            success, stdout, _ = run_command(echo_cmd, shell=True, timeout=5)
            
            if success or "data:" in stdout:
                print_pass("Messages are being published successfully")
                result = True
            else:
                print_fail("Could not receive messages")
                result = False
        else:
            print_fail("/chatter topic not found")
            result = False
        
        # Cleanup
        pub_proc.terminate()
        pub_proc.wait(timeout=2)
        
        return result
        
    except Exception as e:
        print_fail(f"Test failed: {str(e)}")
        return False

def test_code_quality():
    """Test 8: Check for basic code quality"""
    print_test("Testing Code Quality")
    
    home = Path.home()
    publisher_py = home / "ros2_ws" / "src" / "my_first_pkg" / "my_first_pkg" / "simple_publisher.py"
    subscriber_py = home / "ros2_ws" / "src" / "my_first_pkg" / "my_first_pkg" / "simple_subscriber.py"
    
    checks_passed = 0
    total_checks = 0
    
    for filename, filepath in [("Publisher", publisher_py), ("Subscriber", subscriber_py)]:
        if not filepath.exists():
            continue
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check for key elements
        checks = {
            "class definition": "class Simple" in content,
            "rclpy import": "import rclpy" in content,
            "Node inheritance": "(Node)" in content,
            "main function": "def main" in content,
        }
        
        for check_name, passed in checks.items():
            total_checks += 1
            if passed:
                checks_passed += 1
    
    if checks_passed == total_checks:
        print_pass(f"Code structure looks good ({checks_passed}/{total_checks} checks)")
        return True
    else:
        print_info(f"Some code structure issues ({checks_passed}/{total_checks} checks passed)")
        return False

def main():
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}Chapter 3: Python Pub/Sub - Test Suite{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
    
    tests = [
        ("Workspace Structure", test_workspace_exists, True),
        ("Package Creation", test_package_exists, True),
        ("Python Node Files", test_python_files_exist, True),
        ("Entry Points", test_entry_points, True),
        ("Package Build", test_package_builds, True),
        ("Node Discoverability", test_nodes_executable, True),
        ("Message Flow", test_message_flow, True),
        ("Code Quality", test_code_quality, False),
    ]
    
    results = []
    for test_name, test_func, required in tests:
        try:
            passed = test_func()
            results.append((test_name, passed, required))
        except Exception as e:
            print_fail(f"Test crashed: {str(e)}")
            results.append((test_name, False, required))
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}Test Summary{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    required_passed = sum(1 for _, passed, required in results if required and passed)
    required_total = sum(1 for _, _, required in results if required)
    
    for test_name, passed, required in results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if passed else f"{Colors.RED}FAIL{Colors.RESET}"
        req_str = "[REQUIRED]" if required else "[OPTIONAL]"
        print(f"{status} {req_str:12} {test_name}")
    
    print(f"\n{Colors.BOLD}Required Tests:{Colors.RESET} {required_passed}/{required_total}")
    
    if required_passed == required_total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL REQUIRED TESTS PASSED!{Colors.RESET}")
        print(f"\n{Colors.BOLD}Excellent work! You've created your first ROS2 Python nodes!{Colors.RESET}")
        print(f"{Colors.BOLD}Ready for Chapter 4: C++ Publishers & Subscribers{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Review the chapter and fix the issues above.{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
