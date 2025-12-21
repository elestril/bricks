"""
Tests for lib.globals module.

Tests the global constants and path utilities used throughout the brick
configuration system.
"""

import pathlib
import unittest
from unittest.mock import patch, MagicMock
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from lib.globals import BASEDIR, U, scadpath


class TestGlobals(unittest.TestCase):
    """Test cases for the globals module."""

    def test_basedir_is_pathlib_path(self):
        """BASEDIR should be a pathlib.Path object."""
        self.assertIsInstance(BASEDIR, pathlib.Path)

    def test_basedir_points_to_project_root(self):
        """BASEDIR should point to the project root (2 levels up from lib/)."""
        # BASEDIR should contain expected project directories
        expected_dirs = ['bin', 'configs', 'scad']
        basedir_absolute = BASEDIR.resolve()

        # At least some of these directories should exist
        existing_dirs = [d for d in expected_dirs if (basedir_absolute / d).exists()]
        self.assertGreater(len(existing_dirs), 0,
                          "BASEDIR should contain at least some project directories")

    def test_grid_unit_constant(self):
        """U constant should be 12.7mm (0.5 inches)."""
        self.assertEqual(U, 12.7)
        self.assertIsInstance(U, float)

    def test_scadpath_returns_path(self):
        """scadpath() should return a pathlib.Path."""
        with patch('lib.globals.FLAGS') as mock_flags:
            mock_flags.scadpath = str(BASEDIR / 'scad')
            result = scadpath()
            self.assertIsInstance(result, pathlib.Path)

    def test_scadpath_caches_result(self):
        """scadpath() should cache the result for performance."""
        with patch('lib.globals.FLAGS') as mock_flags:
            mock_flags.scadpath = str(BASEDIR / 'scad')

            # Reset the cache
            import lib.globals
            lib.globals._SCADPATH = None

            # First call
            result1 = scadpath()
            # Second call should return the same object (cached)
            result2 = scadpath()

            self.assertIs(result1, result2,
                         "scadpath() should return cached result")

    def test_scadpath_resolves_to_absolute_path(self):
        """scadpath() should return an absolute path."""
        with patch('lib.globals.FLAGS') as mock_flags:
            mock_flags.scadpath = str(BASEDIR / 'scad')

            # Reset the cache
            import lib.globals
            lib.globals._SCADPATH = None

            result = scadpath()
            self.assertTrue(result.is_absolute(),
                          "scadpath() should return an absolute path")


if __name__ == '__main__':
    unittest.main()
