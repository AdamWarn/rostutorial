#!/usr/bin/env python3
"""
ROS2 SLAM Robot Course - Master Test Runner

Runs all chapter tests and provides comprehensive results.
Usage:
    python3 run_tests.py              # Run all tests
    python3 run_tests.py 1 3 5        # Run specific chapters
    python3 run_tests.py --verbose    # Detailed output
"""

import subprocess
import sys
import time
from pathlib import Path
import argparse

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class TestRunner:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = []
        self.course_dir = Path(__file__).parent / "chapters"
        
    def print_header(self):
        """Print test suite header"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}  ROS2 SLAM Robot Course - Automated Test Suite{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}\n")
        
    def print_summary(self):
        """Print test results summary"""
        passed = sum(1 for r in self.results if r['passed'])
        failed = sum(1 for r in self.results if not r['passed'])
        total = len(self.results)
        
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}Test Summary:{Colors.RESET}\n")
        
        for result in self.results:
            status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if result['passed'] else f"{Colors.RED}✗ FAIL{Colors.RESET}"
            print(f"  {status} - {result['name']}")
            if not result['passed'] and not self.verbose:
                print(f"    {Colors.YELLOW}Run with --verbose for details{Colors.RESET}")
        
        print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
        print(f"  {Colors.GREEN}Passed: {passed}{Colors.RESET}")
        print(f"  {Colors.RED}Failed: {failed}{Colors.RESET}")
        print(f"  Total:  {total}")
        
        percentage = (passed / total * 100) if total > 0 else 0
        print(f"\n{Colors.BOLD}Success Rate: {percentage:.1f}%{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}\n")
        
        return failed == 0
    
    def run_chapter_test(self, chapter_num):
        """Run tests for a specific chapter"""
        # Find chapter directory
        chapter_dirs = list(self.course_dir.glob(f"chapter_{chapter_num:02d}_*"))
        
        if not chapter_dirs:
            print(f"{Colors.YELLOW}⚠ Chapter {chapter_num} not found{Colors.RESET}")
            return None
            
        chapter_dir = chapter_dirs[0]
        chapter_name = chapter_dir.name
        test_file = chapter_dir / "tests" / f"test_chapter_{chapter_num:02d}.py"
        
        if not test_file.exists():
            print(f"{Colors.YELLOW}⚠ No tests for Chapter {chapter_num} ({chapter_name}){Colors.RESET}")
            return None
        
        print(f"\n{Colors.BLUE}{'─'*70}{Colors.RESET}")
        print(f"{Colors.BOLD}Running Chapter {chapter_num}: {chapter_name}{Colors.RESET}")
        print(f"{Colors.BLUE}{'─'*70}{Colors.RESET}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=not self.verbose,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            elapsed = time.time() - start_time
            passed = result.returncode == 0
            
            if self.verbose or not passed:
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr)
            
            status = f"{Colors.GREEN}PASSED{Colors.RESET}" if passed else f"{Colors.RED}FAILED{Colors.RESET}"
            print(f"\n{status} in {elapsed:.2f}s")
            
            self.results.append({
                'chapter': chapter_num,
                'name': f"Chapter {chapter_num}: {chapter_name}",
                'passed': passed,
                'time': elapsed
            })
            
            return passed
            
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}✗ Test timed out after 5 minutes{Colors.RESET}")
            self.results.append({
                'chapter': chapter_num,
                'name': f"Chapter {chapter_num}: {chapter_name}",
                'passed': False,
                'time': 300
            })
            return False
            
        except Exception as e:
            print(f"{Colors.RED}✗ Error running test: {e}{Colors.RESET}")
            self.results.append({
                'chapter': chapter_num,
                'name': f"Chapter {chapter_num}: {chapter_name}",
                'passed': False,
                'time': 0
            })
            return False
    
    def run_all_tests(self, chapter_list=None):
        """Run all chapter tests or specific chapters"""
        self.print_header()
        
        if chapter_list:
            chapters = chapter_list
        else:
            # Find all chapters with tests
            chapters = []
            for chapter_dir in sorted(self.course_dir.glob("chapter_*")):
                try:
                    chapter_num = int(chapter_dir.name.split('_')[1])
                    test_file = chapter_dir / "tests" / f"test_chapter_{chapter_num:02d}.py"
                    if test_file.exists():
                        chapters.append(chapter_num)
                except (IndexError, ValueError):
                    continue
        
        print(f"{Colors.BOLD}Testing {len(chapters)} chapter(s)...{Colors.RESET}\n")
        
        for chapter_num in chapters:
            self.run_chapter_test(chapter_num)
        
        return self.print_summary()

def main():
    parser = argparse.ArgumentParser(
        description='Run ROS2 SLAM Robot Course automated tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run_tests.py              # Run all tests
  python3 run_tests.py 1 3 5        # Test chapters 1, 3, and 5
  python3 run_tests.py --verbose    # Show detailed output
  python3 run_tests.py 1 --verbose  # Test chapter 1 with details
        """
    )
    
    parser.add_argument(
        'chapters',
        nargs='*',
        type=int,
        help='Specific chapter numbers to test (default: all)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed test output'
    )
    
    args = parser.parse_args()
    
    runner = TestRunner(verbose=args.verbose)
    success = runner.run_all_tests(chapter_list=args.chapters if args.chapters else None)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
