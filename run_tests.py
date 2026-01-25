#!/usr/bin/env python3
"""
CCRS Test Runner
Simplified test execution with different test levels
"""
import sys
import subprocess
import argparse

def run_tests(test_type="all", verbose=False):
    """Run pytest with appropriate markers."""

    # Base pytest command
    cmd = ["python", "-m", "pytest"]

    if verbose:
        cmd.append("-v")

    # Add test type filtering
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "api":
        cmd.extend(["-m", "api"])
    elif test_type == "worker":
        cmd.extend(["-m", "worker"])
    elif test_type == "cli":
        cmd.extend(["-m", "cli"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "fast":
        cmd.extend(["-m", "unit or api"])
    elif test_type == "all":
        # Run all tests
        pass
    else:
        print(f"Unknown test type: {test_type}")
        return 1

    # Add test directory
    cmd.append("tests/")

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run CCRS tests")
    parser.add_argument(
        "type",
        nargs="?",
        default="all",
        choices=["unit", "api", "worker", "cli", "integration", "fast", "all"],
        help="Type of tests to run (default: all)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    print(f"🧪 CCRS Test Suite - Running {args.type} tests")
    print("=" * 50)

    exit_code = run_tests(args.type, args.verbose)

    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")

    sys.exit(exit_code)