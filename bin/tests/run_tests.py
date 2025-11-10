#!/usr/bin/env python3
"""
Test runner for the brick configuration system.

This script discovers and runs all tests in the tests/ directory.
Usage:
    python run_tests.py                 # Run all tests
    python run_tests.py -v              # Run with verbose output
    python run_tests.py test_brick      # Run specific test module
"""

import sys
import unittest
import pathlib

# Add parent directory to path for imports
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))


def run_all_tests(verbosity=1, pattern='test_*.py'):
    """
    Discover and run all tests in the tests directory.

    Args:
        verbosity: Verbosity level (0=quiet, 1=normal, 2=verbose)
        pattern: Pattern to match test files

    Returns:
        unittest.TestResult object
    """
    # Discover tests
    loader = unittest.TestLoader()
    start_dir = pathlib.Path(__file__).parent
    suite = loader.discover(start_dir, pattern=pattern)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    return result


def run_specific_test(test_name, verbosity=1):
    """
    Run a specific test module or test case.

    Args:
        test_name: Name of the test module (e.g., 'test_brick')
        verbosity: Verbosity level

    Returns:
        unittest.TestResult object
    """
    loader = unittest.TestLoader()

    # Try to load as module first
    try:
        suite = loader.loadTestsFromName(test_name)
    except (ImportError, AttributeError):
        # Try with 'test_' prefix if not already present
        if not test_name.startswith('test_'):
            test_name = f'test_{test_name}'
        suite = loader.loadTestsFromName(test_name)

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    return result


def main():
    """Main entry point for test runner."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Run tests for brick configuration system'
    )
    parser.add_argument(
        'test',
        nargs='?',
        help='Specific test module to run (e.g., test_brick or brick)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Minimal output'
    )
    parser.add_argument(
        '-p', '--pattern',
        default='test_*.py',
        help='Pattern to match test files (default: test_*.py)'
    )

    args = parser.parse_args()

    # Determine verbosity
    verbosity = 1
    if args.verbose:
        verbosity = 2
    elif args.quiet:
        verbosity = 0

    # Run tests
    if args.test:
        result = run_specific_test(args.test, verbosity)
    else:
        result = run_all_tests(verbosity, args.pattern)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main()
