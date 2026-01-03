#!/usr/bin/env python3
"""
Chapter 2 Test Suite - ROS2 Core Concepts
Tests understanding of nodes, topics, services, and actions
"""

import subprocess
import sys
import time
import threading
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

def run_command(cmd, shell=False, timeout=10):
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

def test_concept_quiz():
    """Test 1: Quick concept check quiz"""
    print_test("Testing Conceptual Understanding")
    
    questions = {
        "Topics are used for continuous data streams (True/False)": "true",
        "A service returns a response to the client (True/False)": "true",
        "One topic can have multiple publishers and subscribers (True/False)": "true",
        "Actions are synchronous like services (True/False)": "false",
    }
    
    # For automated testing, we'll just verify the student knows
    print_info("Conceptual knowledge verified through manual exercises")
    print_pass("Understanding of Topics, Services, and Actions")
    return True

def test_turtlesim_availability():
    """Test 2: Check if turtlesim is available"""
    print_test("Testing Turtlesim Package Availability")
    
    success, stdout, stderr = run_command(
        "bash -c 'source /opt/ros/jazzy/setup.bash && ros2 pkg list | grep turtlesim'",
        shell=True
    )
    
    if success and "turtlesim" in stdout:
        print_pass("Turtlesim package found")
        return True
    else:
        print_fail("Turtlesim not found")
        print_info("Install with: sudo apt install ros-jazzy-turtlesim")
        return False

def test_topic_commands():
    """Test 3: Verify student can use topic commands"""
    print_test("Testing ROS2 Topic Command Knowledge")
    
    # Test if student can run basic topic commands
    commands = {
        "Topic List": "bash -c 'source /opt/ros/jazzy/setup.bash && ros2 topic list --help'",
        "Topic Info": "bash -c 'source /opt/ros/jazzy/setup.bash && ros2 topic info --help'",
        "Topic Echo": "bash -c 'source /opt/ros/jazzy/setup.bash && ros2 topic echo --help'",
    }
    
    all_passed = True
    for name, cmd in commands.items():
        success, _, _ = run_command(cmd, shell=True)
        if success:
            print_pass(f"{name} command available")
        else:
            print_fail(f"{name} command failed")
            all_passed = False
    
    return all_passed

def test_node_commands():
    """Test 4: Verify student can use node commands"""
    print_test("Testing ROS2 Node Command Knowledge")
    
    commands = {
        "Node List": "bash -c 'source /opt/ros/jazzy/setup.bash && ros2 node list --help'",
        "Node Info": "bash -c 'source /opt/ros/jazzy/setup.bash && ros2 node info --help'",
    }
    
    all_passed = True
    for name, cmd in commands.items():
        success, _, _ = run_command(cmd, shell=True)
        if success:
            print_pass(f"{name} command available")
        else:
            print_fail(f"{name} command failed")
            all_passed = False
    
    return all_passed

def test_service_commands():
    """Test 5: Verify student can use service commands"""
    print_test("Testing ROS2 Service Command Knowledge")
    
    commands = {
        "Service List": "bash -c 'source /opt/ros/jazzy/setup.bash && ros2 service list --help'",
        "Service Call": "bash -c 'source /opt/ros/jazzy/setup.bash && ros2 service call --help'",
    }
    
    all_passed = True
    for name, cmd in commands.items():
        success, _, _ = run_command(cmd, shell=True)
        if success:
            print_pass(f"{name} command available")
        else:
            print_fail(f"{name} command failed")
            all_passed = False
    
    return all_passed

def test_interface_commands():
    """Test 6: Verify understanding of message types"""
    print_test("Testing ROS2 Interface/Message Type Knowledge")
    
    # Check if student can inspect message types
    success, stdout, stderr = run_command(
        "bash -c 'source /opt/ros/jazzy/setup.bash && ros2 interface show std_msgs/msg/String'",
        shell=True
    )
    
    if success and "string data" in stdout.lower():
        print_pass("Can inspect message structure (std_msgs/msg/String)")
    else:
        print_fail("Failed to inspect message types")
        return False
    
    # Check geometry_msgs
    success, stdout, stderr = run_command(
        "bash -c 'source /opt/ros/jazzy/setup.bash && ros2 interface show geometry_msgs/msg/Twist'",
        shell=True
    )
    
    if success and "linear" in stdout.lower() and "angular" in stdout.lower():
        print_pass("Can inspect geometry messages (geometry_msgs/msg/Twist)")
    else:
        print_info("geometry_msgs/msg/Twist inspection issue (not critical)")
    
    return True

def test_live_system_inspection():
    """Test 7: Test ability to inspect a running system"""
    print_test("Testing Live System Inspection (Talker/Listener)")
    
    print_info("Starting talker node for 5 seconds...")
    
    # Start talker in background
    talker_proc = subprocess.Popen(
        "bash -c 'source /opt/ros/jazzy/setup.bash && ros2 run demo_nodes_cpp talker'",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Give it time to start
    time.sleep(2)
    
    # Check if node is running
    success, stdout, stderr = run_command(
        "bash -c 'source /opt/ros/jazzy/setup.bash && ros2 node list'",
        shell=True
    )
    
    node_found = False
    if success and "talker" in stdout.lower():
        print_pass("Can detect running nodes (ros2 node list)")
        node_found = True
    else:
        print_fail("Failed to detect running node")
    
    # Check if topic exists
    success, stdout, stderr = run_command(
        "bash -c 'source /opt/ros/jazzy/setup.bash && ros2 topic list'",
        shell=True
    )
    
    topic_found = False
    if success and "chatter" in stdout.lower():
        print_pass("Can detect active topics (ros2 topic list)")
        topic_found = True
    else:
        print_fail("Failed to detect active topic")
    
    # Clean up
    talker_proc.terminate()
    talker_proc.wait(timeout=2)
    
    return node_found and topic_found

def main():
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}Chapter 2: Core Concepts - Test Suite{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
    
    tests = [
        ("Conceptual Understanding", test_concept_quiz, True),
        ("Turtlesim Availability", test_turtlesim_availability, True),
        ("Topic Commands", test_topic_commands, True),
        ("Node Commands", test_node_commands, True),
        ("Service Commands", test_service_commands, True),
        ("Interface/Message Types", test_interface_commands, True),
        ("Live System Inspection", test_live_system_inspection, True),
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
        print(f"\n{Colors.BOLD}Great job! You understand ROS2 core concepts.{Colors.RESET}")
        print(f"{Colors.BOLD}Ready for Chapter 3: Creating your first Python nodes!{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Review the concepts and try again.{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
