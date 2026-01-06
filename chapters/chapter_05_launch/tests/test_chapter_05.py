#!/usr/bin/env python3
"""
Chapter 5 Test Suite - Launch Files & Parameters
Tests launch file functionality and parameter configuration
"""

import subprocess
import sys
import time
import os
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

def run_command(cmd, shell=False, timeout=10):
    """Run a command and return success, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd if isinstance(cmd, list) else cmd,
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

def test_launch_files_exist():
    """Test 1: Verify launch file examples exist"""
    print_test("Launch File Examples Exist")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    launch_files = [
        "simple.launch.py",
        "params_from_yaml.launch.py",
        "with_arguments.launch.py"
    ]
    
    all_exist = True
    for launch_file in launch_files:
        path = chapter_dir / launch_file
        if path.exists():
            print_pass(f"Found {launch_file}")
        else:
            print_fail(f"Missing {launch_file}")
            all_exist = False
    
    return all_exist

def test_python_launch_syntax():
    """Test 2: Verify launch files have valid Python syntax"""
    print_test("Launch File Syntax")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    launch_files = list(chapter_dir.glob("*.launch.py"))
    
    if not launch_files:
        print_fail("No launch files found")
        return False
    
    all_valid = True
    for launch_file in launch_files:
        # Try to compile the Python file
        try:
            with open(launch_file, 'r') as f:
                compile(f.read(), launch_file.name, 'exec')
            print_pass(f"{launch_file.name} - Valid syntax")
        except SyntaxError as e:
            print_fail(f"{launch_file.name} - Syntax error: {e}")
            all_valid = False
    
    return all_valid

def test_launch_file_imports():
    """Test 3: Check if launch files have required imports"""
    print_test("Launch File Imports")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    required_imports = ['launch', 'launch_ros']
    
    all_valid = True
    for launch_file in chapter_dir.glob("*.launch.py"):
        with open(launch_file, 'r') as f:
            content = f.read()
        
        has_imports = True
        for imp in required_imports:
            if f"import {imp}" in content or f"from {imp}" in content:
                continue
            else:
                print_fail(f"{launch_file.name} missing '{imp}' import")
                has_imports = False
                all_valid = False
        
        if has_imports:
            print_pass(f"{launch_file.name} - Has required imports")
    
    return all_valid

def test_yaml_config_exists():
    """Test 4: Verify YAML parameter files exist"""
    print_test("YAML Configuration Files")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    config_dir = chapter_dir / "config"
    
    if not config_dir.exists():
        print_fail("Config directory doesn't exist")
        return False
    
    yaml_files = list(config_dir.glob("*.yaml"))
    
    if yaml_files:
        for yaml_file in yaml_files:
            print_pass(f"Found {yaml_file.name}")
        return True
    else:
        print_fail("No YAML files found in config/")
        return False

def test_yaml_syntax():
    """Test 5: Verify YAML files are valid"""
    print_test("YAML File Syntax")
    
    try:
        import yaml
    except ImportError:
        print_info("PyYAML not installed, skipping YAML validation")
        return True
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    config_dir = chapter_dir / "config"
    
    if not config_dir.exists():
        print_info("No config directory")
        return True
    
    all_valid = True
    for yaml_file in config_dir.glob("*.yaml"):
        try:
            with open(yaml_file, 'r') as f:
                yaml.safe_load(f)
            print_pass(f"{yaml_file.name} - Valid YAML")
        except yaml.YAMLError as e:
            print_fail(f"{yaml_file.name} - YAML error: {e}")
            all_valid = False
    
    return all_valid

def test_parameterized_node():
    """Test 6: Check if parameterized node example exists"""
    print_test("Parameterized Node Example")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    node_file = chapter_dir / "parameterized_talker.py"
    
    if not node_file.exists():
        print_fail("parameterized_talker.py not found")
        return False
    
    # Check if it's executable
    if os.access(node_file, os.X_OK):
        print_pass("Node file is executable")
    else:
        print_info("Node file not executable (may need chmod +x)")
    
    # Check for parameter usage
    with open(node_file, 'r') as f:
        content = f.read()
    
    if 'declare_parameter' in content:
        print_pass("Uses declare_parameter()")
    else:
        print_fail("Doesn't use declare_parameter()")
        return False
    
    if 'get_parameter' in content:
        print_pass("Uses get_parameter()")
    else:
        print_fail("Doesn't use get_parameter()")
        return False
    
    return True

def test_launch_description():
    """Test 7: Check if launch files return LaunchDescription"""
    print_test("Launch Description Function")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    
    all_valid = True
    for launch_file in chapter_dir.glob("*.launch.py"):
        with open(launch_file, 'r') as f:
            content = f.read()
        
        if 'def generate_launch_description():' in content:
            print_pass(f"{launch_file.name} - Has generate_launch_description()")
        else:
            print_fail(f"{launch_file.name} - Missing generate_launch_description()")
            all_valid = False
        
        if 'return LaunchDescription(' in content:
            print_pass(f"{launch_file.name} - Returns LaunchDescription")
        else:
            print_fail(f"{launch_file.name} - Doesn't return LaunchDescription")
            all_valid = False
    
    return all_valid

def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}Chapter 5: Launch Files & Parameters - Test Suite{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    tests = [
        test_launch_files_exist,
        test_python_launch_syntax,
        test_launch_file_imports,
        test_yaml_config_exists,
        test_yaml_syntax,
        test_parameterized_node,
        test_launch_description,
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
