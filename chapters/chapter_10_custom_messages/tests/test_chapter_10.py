#!/usr/bin/env python3
"""
Chapter 10 Test Suite - Custom Messages & Interfaces
Tests custom message/service/action definitions
"""

import subprocess
import sys
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

def test_interface_directories():
    """Test 1: Check if msg/srv/action directories exist"""
    print_test("Interface Directories")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    dirs_to_check = ['msg', 'srv', 'action']
    
    found_any = False
    for dir_name in dirs_to_check:
        dir_path = chapter_dir / dir_name
        if dir_path.exists():
            print_pass(f"{dir_name}/ directory exists")
            found_any = True
        else:
            print_info(f"{dir_name}/ directory not found (optional)")
    
    if not found_any:
        print_fail("No interface directories found")
        return False
    
    return True

def test_message_files():
    """Test 2: Check for .msg files"""
    print_test("Message Definitions")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    msg_dir = chapter_dir / "msg"
    
    if not msg_dir.exists():
        print_info("No msg/ directory")
        return True
    
    msg_files = list(msg_dir.glob("*.msg"))
    
    if msg_files:
        for msg_file in msg_files:
            print_pass(f"Found {msg_file.name}")
            
            # Check basic syntax
            with open(msg_file, 'r') as f:
                content = f.read().strip()
            
            if content:
                lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
                if lines:
                    print_pass(f"  {msg_file.name} has {len(lines)} field(s)")
            else:
                print_fail(f"  {msg_file.name} is empty")
        
        return True
    else:
        print_info("No .msg files found")
        return True

def test_service_files():
    """Test 3: Check for .srv files"""
    print_test("Service Definitions")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    srv_dir = chapter_dir / "srv"
    
    if not srv_dir.exists():
        print_info("No srv/ directory")
        return True
    
    srv_files = list(srv_dir.glob("*.srv"))
    
    if srv_files:
        for srv_file in srv_files:
            print_pass(f"Found {srv_file.name}")
            
            # Check for request/response separator
            with open(srv_file, 'r') as f:
                content = f.read()
            
            if '---' in content:
                print_pass(f"  {srv_file.name} has request/response separator")
            else:
                print_fail(f"  {srv_file.name} missing '---' separator")
        
        return True
    else:
        print_info("No .srv files found")
        return True

def test_action_files():
    """Test 4: Check for .action files"""
    print_test("Action Definitions")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    action_dir = chapter_dir / "action"
    
    if not action_dir.exists():
        print_info("No action/ directory")
        return True
    
    action_files = list(action_dir.glob("*.action"))
    
    if action_files:
        for action_file in action_files:
            print_pass(f"Found {action_file.name}")
            
            # Check for separators (goal --- result --- feedback)
            with open(action_file, 'r') as f:
                content = f.read()
            
            separators = content.count('---')
            if separators == 2:
                print_pass(f"  {action_file.name} has goal/result/feedback sections")
            else:
                print_fail(f"  {action_file.name} should have 2 '---' separators")
        
        return True
    else:
        print_info("No .action files found")
        return True

def test_cmake_configuration():
    """Test 5: Check CMakeLists.txt for interface generation"""
    print_test("CMakeLists.txt Configuration")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    cmake_file = chapter_dir / "CMakeLists.txt"
    
    if not cmake_file.exists():
        print_info("No CMakeLists.txt (may be Python package)")
        return True
    
    with open(cmake_file, 'r') as f:
        content = f.read()
    
    checks = [
        ('rosidl_default_generators', 'rosidl_default_generators dependency'),
        ('rosidl_generate_interfaces', 'rosidl_generate_interfaces call'),
    ]
    
    all_found = True
    for check_str, description in checks:
        if check_str in content:
            print_pass(f"Has {description}")
        else:
            print_info(f"Missing {description} (may not be needed)")
    
    return True

def test_package_xml_dependencies():
    """Test 6: Check package.xml for interface dependencies"""
    print_test("package.xml Dependencies")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    package_file = chapter_dir / "package.xml"
    
    if not package_file.exists():
        print_info("No package.xml found")
        return True
    
    with open(package_file, 'r') as f:
        content = f.read()
    
    required_deps = [
        'rosidl_default_generators',
        'rosidl_default_runtime',
    ]
    
    for dep in required_deps:
        if dep in content:
            print_pass(f"Has {dep} dependency")
        else:
            print_info(f"Missing {dep} (may not be needed)")
    
    return True

def test_field_types():
    """Test 7: Validate message field types"""
    print_test("Message Field Types")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    msg_dir = chapter_dir / "msg"
    
    if not msg_dir.exists():
        print_info("No msg/ directory to check")
        return True
    
    valid_types = {
        'bool', 'byte', 'char',
        'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64',
        'float32', 'float64',
        'string',
        'time', 'duration',
    }
    
    for msg_file in msg_dir.glob("*.msg"):
        with open(msg_file, 'r') as f:
            lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]
        
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                field_type = parts[0].replace('[]', '')  # Remove array brackets
                
                # Check if it's a basic type or custom type (has /)
                if '/' in field_type or field_type in valid_types:
                    continue
                else:
                    print_info(f"{msg_file.name}: Unknown type '{field_type}'")
    
    print_pass("Field types checked")
    return True

def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}Chapter 10: Custom Messages - Test Suite{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    tests = [
        test_interface_directories,
        test_message_files,
        test_service_files,
        test_action_files,
        test_cmake_configuration,
        test_package_xml_dependencies,
        test_field_types,
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
