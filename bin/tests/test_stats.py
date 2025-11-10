"""
Tests for lib.stats module.

Tests the global statistics tracking system used to count operations
like new files, updates, and invalid bricks.
"""

import collections
import unittest
import sys
import pathlib

# Add parent directory to path for imports
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from lib.stats import STATS


class TestStats(unittest.TestCase):
    """Test cases for the stats module."""

    def setUp(self):
        """Set up test fixtures - clear STATS before each test."""
        STATS.clear()

    def test_stats_is_defaultdict(self):
        """STATS should be a defaultdict."""
        self.assertIsInstance(STATS, collections.defaultdict)

    def test_stats_creates_counter_for_new_keys(self):
        """STATS should create a Counter for new keys automatically."""
        # Access a non-existent key
        counter = STATS['test_category']

        # Should get a Counter object
        self.assertIsInstance(counter, collections.Counter)

    def test_stats_increments_values(self):
        """STATS should allow incrementing counter values."""
        STATS['remix']['new'] += 1
        STATS['remix']['new'] += 1
        STATS['remix']['updated'] += 3

        self.assertEqual(STATS['remix']['new'], 2)
        self.assertEqual(STATS['remix']['updated'], 3)

    def test_stats_supports_multiple_categories(self):
        """STATS should support multiple independent categories."""
        STATS['generate']['new'] += 5
        STATS['remix']['new'] += 3
        STATS['total']['new'] += 8

        self.assertEqual(STATS['generate']['new'], 5)
        self.assertEqual(STATS['remix']['new'], 3)
        self.assertEqual(STATS['total']['new'], 8)

    def test_stats_default_value_is_zero(self):
        """Counter values should default to zero for new keys."""
        self.assertEqual(STATS['new_category']['new_operation'], 0)

    def test_stats_can_be_converted_to_dict(self):
        """STATS should be convertible to a regular dict."""
        STATS['test']['op1'] += 1
        STATS['test']['op2'] += 2

        stats_dict = {str(k): dict(v) for (k, v) in STATS.items()}

        self.assertIsInstance(stats_dict, dict)
        self.assertEqual(stats_dict['test']['op1'], 1)
        self.assertEqual(stats_dict['test']['op2'], 2)

    def test_stats_tracks_common_operations(self):
        """STATS should track common brick operations."""
        # Simulate a typical configuration run
        STATS['Blanks']['new'] += 10
        STATS['Blanks']['updated'] += 5
        STATS['Blanks']['unchanged'] += 20
        STATS['total']['new'] += 10
        STATS['total']['updated'] += 5
        STATS['total']['unchanged'] += 20

        self.assertEqual(STATS['Blanks']['new'], 10)
        self.assertEqual(STATS['Blanks']['updated'], 5)
        self.assertEqual(STATS['Blanks']['unchanged'], 20)
        self.assertEqual(STATS['total']['new'], 10)

    def test_stats_can_be_cleared(self):
        """STATS should be clearable for fresh runs."""
        STATS['test']['value'] += 100
        self.assertEqual(STATS['test']['value'], 100)

        STATS.clear()
        self.assertEqual(len(STATS), 0)


if __name__ == '__main__':
    unittest.main()
