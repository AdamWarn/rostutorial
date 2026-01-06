#!/usr/bin/env python3
"""
Chapter 6 Test Suite - URDF Robot Description
Tests URDF file validity and robot description
"""

import subprocess
import sys
import xml.etree.ElementTree as ET
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

def test_urdf_files_exist():
    """Test 1: Verify URDF examples exist"""
    print_test("URDF Files Exist")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    expected_files = [
        "simple_robot.urdf",
        "robot_with_sensors.urdf.xacro",
    ]
    
    all_exist = True
    for urdf_file in expected_files:
        path = chapter_dir / urdf_file
        if path.exists():
            print_pass(f"Found {urdf_file}")
        else:
            print_fail(f"Missing {urdf_file}")
            all_exist = False
    
    return all_exist

def test_urdf_xml_validity():
    """Test 2: Check if URDF files are valid XML"""
    print_test("URDF XML Validity")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    urdf_files = list(chapter_dir.glob("*.urdf"))
    
    if not urdf_files:
        print_info("No .urdf files found (may only have .xacro)")
        return True
    
    all_valid = True
    for urdf_file in urdf_files:
        try:
            tree = ET.parse(urdf_file)
            root = tree.getroot()
            if root.tag == 'robot':
                print_pass(f"{urdf_file.name} - Valid URDF XML")
            else:
                print_fail(f"{urdf_file.name} - Root element is not 'robot'")
                all_valid = False
        except ET.ParseError as e:
            print_fail(f"{urdf_file.name} - XML parse error: {e}")
            all_valid = False
    
    return all_valid

def test_urdf_has_links():
    """Test 3: Verify URDF has link elements"""
    print_test("URDF Contains Links")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    urdf_files = list(chapter_dir.glob("*.urdf"))
    
    if not urdf_files:
        print_info("No .urdf files to check")
        return True
    
    all_valid = True
    for urdf_file in urdf_files:
        try:
            tree = ET.parse(urdf_file)
            links = tree.findall('.//link')
            
            if len(links) > 0:
                print_pass(f"{urdf_file.name} - Has {len(links)} link(s)")
            else:
                print_fail(f"{urdf_file.name} - No links found")
                all_valid = False
        except Exception as e:
            print_fail(f"{urdf_file.name} - Error: {e}")
            all_valid = False
    
    return all_valid

def test_urdf_has_joints():
    """Test 4: Verify URDF has joint elements"""
    print_test("URDF Contains Joints")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    urdf_files = list(chapter_dir.glob("*.urdf"))
    
    if not urdf_files:
        print_info("No .urdf files to check")
        return True
    
    for urdf_file in urdf_files:
        try:
            tree = ET.parse(urdf_file)
            joints = tree.findall('.//joint')
            
            if len(joints) > 0:
                print_pass(f"{urdf_file.name} - Has {len(joints)} joint(s)")
            else:
                print_info(f"{urdf_file.name} - No joints (may be single link)")
        except Exception as e:
            print_fail(f"{urdf_file.name} - Error: {e}")
    
    return True  # Joints are optional for simple robots

def test_xacro_files():
    """Test 5: Check for XACRO files"""
    print_test("XACRO Files")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    xacro_files = list(chapter_dir.glob("*.xacro"))
    
    if xacro_files:
        for xacro_file in xacro_files:
            print_pass(f"Found {xacro_file.name}")
        
        # Check if xacro namespace is used
        for xacro_file in xacro_files:
            with open(xacro_file, 'r') as f:
                content = f.read()
            if 'xmlns:xacro=' in content:
                print_pass(f"{xacro_file.name} - Has xacro namespace")
            else:
                print_info(f"{xacro_file.name} - No xacro namespace (might be plain URDF)")
        
        return True
    else:
        print_info("No .xacro files found (may only use plain URDF)")
        return True

def test_urdf_check_tool():
    """Test 6: Use check_urdf tool if available"""
    print_test("URDF Validation Tool")
    
    # Check if check_urdf is available
    result = subprocess.run(
        ['which', 'check_urdf'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print_info("check_urdf not installed (optional)")
        print_info("Install with: sudo apt install liburdfdom-tools")
        return True
    
    print_pass("check_urdf tool found")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    urdf_files = list(chapter_dir.glob("*.urdf"))
    
    all_valid = True
    for urdf_file in urdf_files:
        result = subprocess.run(
            ['check_urdf', str(urdf_file)],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print_pass(f"{urdf_file.name} - Passed check_urdf")
        else:
            print_fail(f"{urdf_file.name} - Failed check_urdf")
            print_info(f"  {result.stderr}")
            all_valid = False
    
    return all_valid

def test_visual_and_collision():
    """Test 7: Check for visual and collision geometry"""
    print_test("Visual and Collision Geometry")
    
    chapter_dir = Path(__file__).parent.parent / "examples"
    urdf_files = list(chapter_dir.glob("*.urdf"))
    
    if not urdf_files:
        print_info("No .urdf files to check")
        return True
    
    for urdf_file in urdf_files:
        try:
            tree = ET.parse(urdf_file)
            visuals = tree.findall('.//visual')
            collisions = tree.findall('.//collision')
            
            if visuals:
                print_pass(f"{urdf_file.name} - Has visual geometry")
            else:
                print_info(f"{urdf_file.name} - No visual geometry")
            
            if collisions:
                print_pass(f"{urdf_file.name} - Has collision geometry")
            else:
                print_info(f"{urdf_file.name} - No collision geometry (optional)")
        except Exception as e:
            print_fail(f"{urdf_file.name} - Error: {e}")
    
    return True

def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}Chapter 6: URDF Robot Description - Test Suite{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    tests = [
        test_urdf_files_exist,
        test_urdf_xml_validity,
        test_urdf_has_links,
        test_urdf_has_joints,
        test_xacro_files,
        test_urdf_check_tool,
        test_visual_and_collision,
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
