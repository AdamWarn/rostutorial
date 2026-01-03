#!/usr/bin/env python3
"""
Chapter 4 Test Suite - C++ Publishers & Subscribers
Tests C++ package creation, compilation, and execution
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

def run_command(cmd, shell=False, timeout=60):
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

def test_cpp_package_exists():
    """Test 1: Check if C++ package exists"""
    print_test("Testing C++ Package Creation")
    
    home = Path.home()
    pkg_path = home / "ros2_ws" / "src" / "my_cpp_pkg"
    
    if pkg_path.exists():
        print_pass("Package 'my_cpp_pkg' found")
        
        files_to_check = [
            "package.xml",
            "CMakeLists.txt",
            "src"
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
        print_fail("Package 'my_cpp_pkg' not found")
        print_info("Create with: ros2 pkg create --build-type ament_cmake my_cpp_pkg --dependencies rclcpp std_msgs")
        return False

def test_cpp_files_exist():
    """Test 2: Check if C++ source files exist"""
    print_test("Testing C++ Source Files")
    
    home = Path.home()
    src_path = home / "ros2_ws" / "src" / "my_cpp_pkg" / "src"
    
    nodes = {
        "simple_publisher.cpp": "Publisher node",
        "simple_subscriber.cpp": "Subscriber node",
    }
    
    all_exist = True
    for filename, description in nodes.items():
        filepath = src_path / filename
        if filepath.exists():
            print_pass(f"{description} ({filename}) exists")
        else:
            print_fail(f"{description} ({filename}) missing")
            all_exist = False
    
    return all_exist

def test_package_builds():
    """Test 3: Check if C++ package builds"""
    print_test("Testing C++ Package Build")
    
    home = Path.home()
    workspace = home / "ros2_ws"
    
    if not workspace.exists():
        print_fail("Workspace doesn't exist")
        return False
    
    print_info("Building my_cpp_pkg (may take 30-60 seconds)...")
    
    success, stdout, stderr = run_command(
        f"bash -c 'cd {workspace} && source /opt/ros/jazzy/setup.bash && colcon build --packages-select my_cpp_pkg'",
        shell=True,
        timeout=120
    )
    
    if success and ("Finished" in stdout or "built" in stdout.lower()):
        print_pass("C++ package builds successfully")
        return True
    else:
        print_fail("C++ package build failed")
        if stderr:
            print_info(f"Error (first 300 chars): {stderr[:300]}")
        return False

def test_executables_exist():
    """Test 4: Check if executables were created"""
    print_test("Testing Executable Creation")
    
    home = Path.home()
    install_path = home / "ros2_ws" / "install" / "my_cpp_pkg" / "lib" / "my_cpp_pkg"
    
    if not install_path.exists():
        print_fail("Install directory not found - package may not be built")
        return False
    
    executables = ["simple_publisher", "simple_subscriber"]
    all_exist = True
    
    for exe in executables:
        exe_path = install_path / exe
        if exe_path.exists():
            print_pass(f"{exe} executable created")
        else:
            print_fail(f"{exe} executable missing")
            all_exist = False
    
    return all_exist

def test_nodes_run():
    """Test 5: Test if nodes can run"""
    print_test("Testing Node Execution")
    
    home = Path.home()
    workspace = home / "ros2_ws"
    
    print_info("Starting C++ publisher...")
    
    pub_cmd = f"bash -c 'source /opt/ros/jazzy/setup.bash && source {workspace}/install/setup.bash && timeout 3 ros2 run my_cpp_pkg simple_publisher'"
    
    success, stdout, stderr = run_command(pub_cmd, shell=True, timeout=5)
    
    # Even if timeout, if it started publishing that's success
    if "Publishing" in stdout or "Simple Publisher" in stdout:
        print_pass("C++ publisher runs and publishes messages")
        return True
    else:
        print_fail("C++ publisher failed to run")
        if stderr:
            print_info(f"Error: {stderr[:200]}")
        return False

def main():
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}Chapter 4: C++ Pub/Sub - Test Suite{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
    
    tests = [
        ("C++ Package Exists", test_cpp_package_exists, True),
        ("C++ Source Files", test_cpp_files_exist, True),
        ("Package Builds", test_package_builds, True),
        ("Executables Created", test_executables_exist, True),
        ("Nodes Execute", test_nodes_run, True),
    ]
    
    results = []
    for test_name, test_func, required in tests:
        try:
            passed = test_func()
            results.append((test_name, passed, required))
        except Exception as e:
            print_fail(f"Test crashed: {str(e)}")
            results.append((test_name, False, required))
    
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
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.RESET}")
        print(f"\n{Colors.BOLD}Great! You've mastered C++ in ROS2!{Colors.RESET}")
        print(f"{Colors.BOLD}Ready for Chapter 5: Launch Files & Parameters{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Review the chapter and fix issues above.{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
