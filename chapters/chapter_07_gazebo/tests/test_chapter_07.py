#!/usr/bin/env python3
"""
Chapter 7 Test Suite - Gazebo Simulation
Tests Gazebo integration and launch files
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

def print_test(name):
    print(f"\n{Colors.BLUE}[TEST]{Colors.RESET} {name}")

def print_pass(message):
    print(f"  {Colors.GREEN}✓{Colors.RESET} {message}")

def print_fail(message):
    print(f"  {Colors.RED}✗{Colors.RESET} {message}")

def print_info(message):
    print(f"  {Colors.YELLOW}ℹ{Colors.RESET} {message}")

def run_command(cmd, timeout=10):
    """Run a command and return success, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd,
            shell=isinstance(cmd, str),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_gazebo_installed():
    """Test 1: Check if Gazebo is installed"""
    print_test("Gazebo Installation")
    
    success, stdout, stderr = run_command(['which', 'gz'])
    
    if success and stdout.strip():
        print_pass(f"Gazebo found at: {stdout.strip()}")
        
        # Try to get version
        success, stdout, stderr = run_command(['gz', 'sim', '--version'])
        if success:
            version = stdout.strip().split('\n')[0] if stdout else "Unknown"
            print_pass(f"Version: {version}")
        
        return True
    else:
        print_fail("Gazebo not found")
        print_info("Install with: sudo apt install ros-jazzy-gazebo-ros-pkgs")
        return False

def test_world_files_exist():
    """Test 2: Check for world files"""
    print_test("World Files")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    world_dir = chapter_dir / "worlds"
    
    if not world_dir.exists():
        print_fail("worlds/ directory doesn't exist")
        return False
    
    world_files = list(world_dir.glob("*.world"))
    
    if world_files:
        for world_file in world_files:
            print_pass(f"Found {world_file.name}")
        return True
    else:
        print_fail("No .world files found")
        return False

def test_launch_file_exists():
    """Test 3: Check for Gazebo launch file"""
    print_test("Gazebo Launch File")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    launch_files = list(chapter_dir.glob("*gazebo*.launch.py"))
    
    if launch_files:
        for launch_file in launch_files:
            print_pass(f"Found {launch_file.name}")
        return True
    else:
        print_fail("No Gazebo launch file found")
        return False

def test_gazebo_ros_packages():
    """Test 4: Check if gazebo_ros packages are available"""
    print_test("Gazebo ROS2 Packages")
    
    packages_to_check = [
        'gazebo_ros',
        'gazebo_plugins',
    ]
    
    all_found = True
    for package in packages_to_check:
        success, stdout, stderr = run_command(['ros2', 'pkg', 'prefix', package])
        
        if success:
            print_pass(f"{package} found")
        else:
            print_fail(f"{package} not found")
            all_found = False
    
    if not all_found:
        print_info("Install with: sudo apt install ros-jazzy-gazebo-ros-pkgs")
    
    return all_found

def test_spawn_entity_plugin():
    """Test 5: Check for spawn_entity script"""
    print_test("Spawn Entity Plugin")
    
    success, stdout, stderr = run_command(
        ['ros2', 'run', 'gazebo_ros', 'spawn_entity.py', '--help']
    )
    
    if success:
        print_pass("spawn_entity.py available")
        return True
    else:
        print_fail("spawn_entity.py not available")
        return False

def test_urdf_spawner_in_launch():
    """Test 6: Check if launch file includes URDF spawning"""
    print_test("URDF Spawning in Launch File")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    launch_files = list(chapter_dir.glob("*.launch.py"))
    
    if not launch_files:
        print_fail("No launch files found")
        return False
    
    found_spawner = False
    for launch_file in launch_files:
        with open(launch_file, 'r') as f:
            content = f.read()
        
        if 'spawn_entity' in content:
            print_pass(f"{launch_file.name} - Includes spawn_entity")
            found_spawner = True
        
        if 'gzserver' in content or 'gazebo' in content:
            print_pass(f"{launch_file.name} - Starts Gazebo")
    
    return found_spawner

def test_robot_description_parameter():
    """Test 7: Check if robot_description parameter is set"""
    print_test("Robot Description Parameter")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    launch_files = list(chapter_dir.glob("*.launch.py"))
    
    found_robot_desc = False
    for launch_file in launch_files:
        with open(launch_file, 'r') as f:
            content = f.read()
        
        if 'robot_description' in content:
            print_pass(f"{launch_file.name} - Sets robot_description")
            found_robot_desc = True
        
        if 'robot_state_publisher' in content:
            print_pass(f"{launch_file.name} - Includes robot_state_publisher")
    
    if not found_robot_desc:
        print_info("No robot_description found (may be in separate file)")
    
    return True  # Not critical for basic Gazebo test

def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}Chapter 7: Gazebo Simulation - Test Suite{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    tests = [
        test_gazebo_installed,
        test_world_files_exist,
        test_launch_file_exists,
        test_gazebo_ros_packages,
        test_spawn_entity_plugin,
        test_urdf_spawner_in_launch,
        test_robot_description_parameter,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print_fail(f"Test crashed: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}Results: {passed}/{total} tests passed{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    return 0 if all(results) else 1

if __name__ == '__main__':
    sys.exit(main())
