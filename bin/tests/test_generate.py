"""
Tests for lib.generate module.

Tests the Generate class which creates bricks by iterating over
parameter combinations and applying conditional filters.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import pathlib

# Add parent directory to path for imports
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from lib.generate import Generate
from lib.brick import Brick


class TestGenerate(unittest.TestCase):
    """Test cases for the Generate class."""

    def setUp(self):
        """Set up test fixtures."""
        self.simple_config = {
            'generate': {
                'x': [1, 2],
                'y': [1, 2]
            },
            'config': {
                'set': 'TestSet',
                'type': 'Plate'
            }
        }

    @patch('lib.generate.FLAGS')
    def test_generate_creation(self, mock_flags):
        """Generate should be created with name and config."""
        mock_flags.generate = []

        gen = Generate('TestGen', self.simple_config)

        self.assertEqual(gen.name, 'TestGen')
        self.assertEqual(gen.generate, {'x': [1, 2], 'y': [1, 2]})
        self.assertEqual(gen.config, {'set': 'TestSet', 'type': 'Plate'})

    @patch('lib.generate.FLAGS')
    def test_generate_raises_if_not_enabled(self, mock_flags):
        """Generate should raise ValueError if not in FLAGS.generate."""
        mock_flags.generate = ['OtherGen']  # Different name

        with self.assertRaises(ValueError) as context:
            Generate('TestGen', self.simple_config)

        self.assertIn('not enabled', str(context.exception))

    @patch('lib.generate.FLAGS')
    def test_generate_succeeds_if_enabled(self, mock_flags):
        """Generate should succeed if name is in FLAGS.generate."""
        mock_flags.generate = ['TestGen']

        gen = Generate('TestGen', self.simple_config)

        self.assertEqual(gen.name, 'TestGen')

    @patch('lib.generate.FLAGS')
    def test_generate_bricks_cartesian_product(self, mock_flags):
        """Generate.bricks should produce Cartesian product of parameters."""
        mock_flags.generate = []

        gen = Generate('TestGen', self.simple_config)
        bricks = list(gen.bricks)

        # Should generate 2x2 = 4 bricks
        self.assertEqual(len(bricks), 4)

        # Check that all bricks are Brick instances
        for brick in bricks:
            self.assertIsInstance(brick, Brick)

    @patch('lib.generate.FLAGS')
    def test_generate_bricks_have_correct_parameters(self, mock_flags):
        """Generated bricks should have correct parameter combinations."""
        mock_flags.generate = []

        gen = Generate('TestGen', self.simple_config)
        bricks = list(gen.bricks)

        # Extract (x, y) tuples from bricks
        sizes = [(b.x, b.y) for b in bricks]

        # Should have all combinations
        expected_sizes = [(1, 1), (1, 2), (2, 1), (2, 2)]
        self.assertEqual(sorted(sizes), sorted(expected_sizes))

    @patch('lib.generate.FLAGS')
    def test_generate_with_condition_filter(self, mock_flags):
        """Generate should filter bricks based on condition."""
        mock_flags.generate = []

        config_with_condition = {
            'generate': {
                'x': [1, 2, 3],
                'y': [1, 2, 3]
            },
            'condition': '{x} >= {y}',  # Only x >= y
            'config': {
                'set': 'TestSet',
                'type': 'Plate'
            }
        }

        gen = Generate('TestGen', config_with_condition)
        bricks = list(gen.bricks)

        # Should only generate bricks where x >= y
        # (1,1), (2,1), (2,2), (3,1), (3,2), (3,3) = 6 bricks
        self.assertEqual(len(bricks), 6)

        # Verify all bricks meet the condition
        for brick in bricks:
            self.assertGreaterEqual(brick.x, brick.y)

    @patch('lib.generate.FLAGS')
    def test_generate_default_condition_is_true(self, mock_flags):
        """Generate should default to 'True' condition if not specified."""
        mock_flags.generate = []

        config_no_condition = {
            'generate': {
                'x': [1, 2]
            },
            'config': {
                'set': 'TestSet',
                'type': 'Plate',
                'y': 1
            }
        }

        gen = Generate('TestGen', config_no_condition)

        # Default condition is 'True'
        self.assertEqual(gen.condition, 'True')

        # Should generate all bricks
        bricks = list(gen.bricks)
        self.assertEqual(len(bricks), 2)

    @patch('lib.generate.FLAGS')
    def test_generate_with_family_parameter(self, mock_flags):
        """Generate should handle family parameter in generate dict."""
        mock_flags.generate = []

        config_with_family = {
            'generate': {
                'x': [1, 2],
                'family': ['HexR', 'HexS']
            },
            'config': {
                'set': 'TestSet',
                'type': 'Tile',
                'y': 0
            }
        }

        gen = Generate('TestGen', config_with_family)
        bricks = list(gen.bricks)

        # Should generate 2x2 = 4 bricks
        self.assertEqual(len(bricks), 4)

        # Check families
        families = [b.family for b in bricks]
        self.assertIn('HexR', families)
        self.assertIn('HexS', families)

    @patch('lib.generate.FLAGS')
    def test_generate_bricks_inherit_base_config(self, mock_flags):
        """Generated bricks should inherit base config parameters."""
        mock_flags.generate = []

        config_with_base = {
            'generate': {
                'x': [1]
            },
            'config': {
                'set': 'MySet',
                'type': 'Wall',
                'y': 1,
                'texture': 'wood.png'
            }
        }

        gen = Generate('TestGen', config_with_base)
        bricks = list(gen.bricks)

        self.assertEqual(len(bricks), 1)
        brick = bricks[0]

        self.assertEqual(brick.set, 'MySet')
        self.assertEqual(brick.type, 'Wall')
        self.assertEqual(brick.texture, 'wood.png')

    @patch('lib.generate.FLAGS')
    def test_generate_bricks_cached_property(self, mock_flags):
        """Generate.bricks should be a cached property."""
        mock_flags.generate = []

        gen = Generate('TestGen', self.simple_config)

        # First access
        bricks1 = gen.bricks
        # Second access should return same iterator
        bricks2 = gen.bricks

        # Both should be the same cached object
        self.assertIs(bricks1, bricks2)

    @patch('lib.generate.FLAGS')
    def test_generate_single_parameter(self, mock_flags):
        """Generate should work with single parameter."""
        mock_flags.generate = []

        config_single = {
            'generate': {
                'x': [1, 2, 3, 4]
            },
            'config': {
                'set': 'TestSet',
                'type': 'Wall',
                'y': 1
            }
        }

        gen = Generate('TestGen', config_single)
        bricks = list(gen.bricks)

        # Should generate 4 bricks
        self.assertEqual(len(bricks), 4)

        # Check x values
        x_values = [b.x for b in bricks]
        self.assertEqual(x_values, [1, 2, 3, 4])

    @patch('lib.generate.FLAGS')
    def test_generate_complex_condition(self, mock_flags):
        """Generate should handle complex conditions."""
        mock_flags.generate = []

        config_complex = {
            'generate': {
                'x': [1, 2, 3],
                'y': [1, 2, 3]
            },
            'condition': '{x} * {y} <= 4',  # Area <= 4
            'config': {
                'set': 'TestSet',
                'type': 'Plate'
            }
        }

        gen = Generate('TestGen', config_complex)
        bricks = list(gen.bricks)

        # Verify all bricks meet the condition
        for brick in bricks:
            self.assertLessEqual(brick.x * brick.y, 4)

        # Should have: (1,1), (1,2), (1,3), (2,1), (2,2), (3,1) = 6 bricks
        self.assertEqual(len(bricks), 6)


if __name__ == '__main__':
    unittest.main()
