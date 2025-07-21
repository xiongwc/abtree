#!/usr/bin/env python3
"""
Test Runner Script

Provides multiple test running methods including unit tests, integration tests, coverage tests, etc.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_pytest(args):
    """Run pytest tests"""
    cmd = ["python", "-m", "pytest"] + args
    print(f"Running command: {' '.join(cmd)}")
    return subprocess.run(cmd)


def run_unit_tests():
    """Run unit tests"""
    print("🧪 Running unit tests...")
    args = ["tests/test_core.py", "tests/test_nodes.py", "-v", "--tb=short"]
    return run_pytest(args)


def run_integration_tests():
    """Run integration tests"""
    print("🔗 Running integration tests...")
    args = ["tests/test_behavior_tree.py", "-v", "--tb=short"]
    return run_pytest(args)


def run_all_tests():
    """Run all tests"""
    print("📋 Running all tests...")
    args = ["tests/", "-v", "--tb=short"]
    return run_pytest(args)


def run_coverage_tests():
    """Run coverage tests"""
    print("📊 Running coverage tests...")
    args = [
        "tests/",
        "--cov=abtree",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=80",
        "-v",
    ]
    return run_pytest(args)


def run_specific_test(test_file):
    """Run specific test file"""
    print(f"🎯 Running specific test: {test_file}")
    args = [test_file, "-v", "--tb=short"]
    return run_pytest(args)


def run_marked_tests(marker):
    """Run marked tests"""
    print(f"🏷️ Running marked tests: {marker}")
    args = ["tests/", f"-m {marker}", "-v", "--tb=short"]
    return run_pytest(args)


def run_parallel_tests():
    """Run tests in parallel"""
    print("⚡ Running tests in parallel...")
    args = ["tests/", "-n", "auto", "-v", "--tb=short"]
    return run_pytest(args)


def run_slow_tests():
    """Run slow tests"""
    print("🐌 Running slow tests...")
    args = ["tests/", "-m", "slow", "-v", "--tb=short"]
    return run_pytest(args)


def run_fast_tests():
    """Run fast tests"""
    print("⚡ Running fast tests...")
    args = ["tests/", "-m", "not slow", "-v", "--tb=short"]
    return run_pytest(args)


def generate_html_report():
    """Generate HTML test report"""
    print("📄 Generating HTML test report...")
    args = ["tests/", "--html=test_report.html", "--self-contained-html", "-v"]
    return run_pytest(args)


def check_test_environment():
    """Check test environment"""
    print("🔍 Checking test environment...")

    # Check if pytest is installed
    try:
        import pytest

        print("✅ pytest is installed")
    except ImportError:
        print("❌ pytest is not installed, please run: pip install pytest")
        return False

    # Check if pytest-cov is installed
    try:
        import coverage

        print("✅ pytest-cov is installed")
    except ImportError:
        print("⚠️ pytest-cov is not installed, coverage tests may not be available")

    # Check if pytest-html is installed
    try:
        import pytest_html

        print("✅ pytest-html is installed")
    except ImportError:
        print("⚠️ pytest-html is not installed, HTML reports may not be available")

    # Check if pytest-xdist is installed
    try:
        import execnet

        print("✅ pytest-xdist is installed")
    except ImportError:
        print("⚠️ pytest-xdist is not installed, parallel tests may not be available")

    return True


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="ABTree Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--coverage", action="store_true", help="Run coverage tests")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--slow", action="store_true", help="Run slow tests")
    parser.add_argument("--fast", action="store_true", help="Run fast tests")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--check", action="store_true", help="Check test environment")
    parser.add_argument("--file", type=str, help="Run specific test file")
    parser.add_argument("--marker", type=str, help="Run marked tests")

    args = parser.parse_args()

    # Check test environment
    if args.check:
        check_test_environment()
        return

    # Check test environment
    if not check_test_environment():
        return

    # Run tests
    if args.unit:
        result = run_unit_tests()
    elif args.integration:
        result = run_integration_tests()
    elif args.all:
        result = run_all_tests()
    elif args.coverage:
        result = run_coverage_tests()
    elif args.parallel:
        result = run_parallel_tests()
    elif args.slow:
        result = run_slow_tests()
    elif args.fast:
        result = run_fast_tests()
    elif args.html:
        result = generate_html_report()
    elif args.file:
        result = run_specific_test(args.file)
    elif args.marker:
        result = run_marked_tests(args.marker)
    else:
        # Default run all tests
        print("📋 Default running all tests...")
        result = run_all_tests()

    # Show results
    if result.returncode == 0:
        print("✅ Tests completed")
    else:
        print("❌ Tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
