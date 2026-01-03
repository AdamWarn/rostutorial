#!/usr/bin/env python3
"""
Chapter 1 Test Suite - Environment Verification
Tests ROS2 Jazzy installation and basic setup
"""

import subprocess
import sys
import os
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
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

def run_command(cmd, shell=False):
    """Run a command and return success, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd if not shell else cmd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_ros2_installation():
    """Test 1: Verify ROS2 Jazzy is installed"""
    print_test("Testing ROS2 Jazzy Installation")
    
    # Check if ROS2 command exists
    success, stdout, stderr = run_command(
        "bash -c 'source /opt/ros/jazzy/setup.bash && ros2 --version'",
        shell=True
    )
    
    if success and "jazzy" in stdout.lower():
        version = stdout.strip()
        print_pass(f"ROS2 Jazzy found: {version}")
        return True
    else:
        print_fail("ROS2 Jazzy not found or not properly installed")
        print_info(f"Error: {stderr}")
        return False

def test_demo_nodes():
    """Test 2: Check if demo nodes packages are available"""
    print_test("Testing Demo Nodes Availability")
    
    success, stdout, stderr = run_command(
        "bash -c 'source /opt/ros/jazzy/setup.bash && ros2 pkg list | grep demo_nodes'",
        shell=True
    )
    
    if success and "demo_nodes_cpp" in stdout and "demo_nodes_py" in stdout:
        print_pass("Demo nodes packages found (demo_nodes_cpp, demo_nodes_py)")
        return True
    else:
        print_fail("Demo nodes packages not found")
        print_info("Install with: sudo apt install ros-jazzy-demo-nodes-cpp ros-jazzy-demo-nodes-py")
        return False

def test_workspace_structure():
    """Test 3: Check if workspace structure exists"""
    print_test("Testing ROS2 Workspace Structure")
    
    home = Path.home()
    workspace = home / "ros2_ws"
    src_dir = workspace / "src"
    
    if workspace.exists() and src_dir.exists():
        print_pass(f"Workspace found at {workspace}")
        print_pass(f"Source directory exists at {src_dir}")
        
        # Check if workspace was built
        install_dir = workspace / "install"
        if install_dir.exists():
            print_pass("Workspace has been built (install/ directory exists)")
        else:
            print_info("Workspace exists but hasn't been built yet")
            print_info("Run: cd ~/ros2_ws && colcon build")
        
        return True
    else:
        print_fail(f"Workspace not found at {workspace}")
        print_info("Create with: mkdir -p ~/ros2_ws/src")
        return False

def test_essential_tools():
    """Test 4: Check essential development tools"""
    print_test("Testing Essential Development Tools")
    
    tools = {
        "colcon": "colcon --version",
        "Python3": "python3 --version",
        "GCC (C++ compiler)": "gcc --version",
    }
    
    all_found = True
    for tool_name, command in tools.items():
        success, stdout, _ = run_command(command, shell=True)
        if success:
            version = stdout.split('\n')[0] if stdout else "installed"
            print_pass(f"{tool_name}: {version}")
        else:
            print_fail(f"{tool_name} not found")
            all_found = False
    
    return all_found

def test_gazebo_installation():
    """Test 5: Check if Gazebo is installed (for simulation)"""
    print_test("Testing Gazebo Simulator Installation")
    
    success, stdout, stderr = run_command(
        "bash -c 'source /opt/ros/jazzy/setup.bash && ros2 pkg list | grep gazebo_ros'",
        shell=True
    )
    
    if success and "gazebo_ros" in stdout:
        print_pass("Gazebo ROS packages found")
        return True
    else:
        print_fail("Gazebo ROS packages not found")
        print_info("Install with: sudo apt install ros-jazzy-gazebo-ros-pkgs")
        print_info("(This is needed for later chapters, not critical now)")
        return False

def test_rviz2():
    """Test 6: Check if RViz2 is installed (for visualization)"""
    print_test("Testing RViz2 Visualization Tool")
    
    success, stdout, stderr = run_command(
        "bash -c 'source /opt/ros/jazzy/setup.bash && ros2 pkg list | grep rviz2'",
        shell=True
    )
    
    if success and "rviz2" in stdout:
        print_pass("RViz2 found")
        return True
    else:
        print_fail("RViz2 not found")
        print_info("Install with: sudo apt install ros-jazzy-rviz2")
        return False

def main():
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}Chapter 1: Environment Setup - Test Suite{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
    
    tests = [
        ("ROS2 Installation", test_ros2_installation, True),
        ("Demo Nodes", test_demo_nodes, True),
        ("Workspace Structure", test_workspace_structure, True),
        ("Development Tools", test_essential_tools, True),
        ("Gazebo Simulator", test_gazebo_installation, False),
        ("RViz2 Visualization", test_rviz2, False),
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
    optional_passed = sum(1 for _, passed, required in results if not required and passed)
    optional_total = sum(1 for _, _, required in results if not required)
    
    for test_name, passed, required in results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if passed else f"{Colors.RED}FAIL{Colors.RESET}"
        req_str = "[REQUIRED]" if required else "[OPTIONAL]"
        print(f"{status} {req_str:12} {test_name}")
    
    print(f"\n{Colors.BOLD}Required Tests:{Colors.RESET} {required_passed}/{required_total}")
    print(f"{Colors.BOLD}Optional Tests:{Colors.RESET} {optional_passed}/{optional_total}")
    
    # Determine overall result
    if required_passed == required_total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL REQUIRED TESTS PASSED!{Colors.RESET}")
        print(f"\n{Colors.BOLD}You're ready to proceed to Chapter 2!{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME REQUIRED TESTS FAILED{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Please fix the issues above before proceeding.{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
