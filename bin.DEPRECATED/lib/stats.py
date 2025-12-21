"""
Statistics tracking for brick configuration operations.

This module provides a global statistics counter to track operations
like new files created, updated files, unchanged files, and invalid bricks.
"""

import collections

# Global statistics counter: two-level defaultdict for tracking operations by category
# Structure: STATS[category][operation] = count
# Example: STATS['remix']['new'] = 5, STATS['total']['updated'] = 12
STATS = collections.defaultdict(collections.Counter)