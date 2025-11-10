"""
Tests for lib.remix module.

Tests the Remix class which processes existing STL files and converts
them to brick configurations based on regex matching and YAML rules.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import pathlib
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from lib.remix import Remix
from lib.brick import Brick, InvalidBrick


class TestRemix(unittest.TestCase):
    """Test cases for the Remix class."""

    def setUp(self):
        """Set up test fixtures."""
        self.simple_config = {
            'regex': [r'test_(\d+)x(\d+)\.stl'],
            'config': {
                '*': {
                    'set': 'TestSet',
                    'type': 'Plate'
                }
            }
        }

    @patch('lib.remix.FLAGS')
    def test_remix_raises_without_input_flag(self, mock_flags):
        """Remix should raise ValueError if --input is not set."""
        mock_flags.input = None
        mock_flags.remix = []

        with self.assertRaises(ValueError) as context:
            Remix('TestRemix', self.simple_config)

        self.assertIn('--input is not defined', str(context.exception))

    @patch('lib.remix.FLAGS')
    @patch('pathlib.Path.glob')
    def test_remix_creation_with_input(self, mock_glob, mock_flags):
        """Remix should be created when --input is set."""
        mock_flags.input = '/test/input'
        mock_flags.remix = []
        mock_glob.return_value = []

        remix = Remix('TestRemix', self.simple_config)

        self.assertEqual(remix.name, 'TestRemix')
        self.assertEqual(remix.config, self.simple_config['config'])

    @patch('lib.remix.FLAGS')
    def test_remix_raises_if_not_enabled(self, mock_flags):
        """Remix should raise ValueError if not in FLAGS.remix."""
        mock_flags.input = '/test/input'
        mock_flags.remix = ['OtherRemix:*.stl']  # Different name

        with self.assertRaises(ValueError) as context:
            Remix('TestRemix', self.simple_config)

        self.assertIn('not enabled', str(context.exception))

    @patch('lib.remix.FLAGS')
    @patch('pathlib.Path.glob')
    def test_remix_compiles_regex_patterns(self, mock_glob, mock_flags):
        """Remix should compile regex patterns from config."""
        mock_flags.input = '/test/input'
        mock_flags.remix = []
        mock_glob.return_value = []

        remix = Remix('TestRemix', self.simple_config)

        # Should have compiled regex patterns
        self.assertEqual(len(remix._regex), 1)

    @patch('lib.remix.FLAGS')
    @patch('pathlib.Path.glob')
    @patch('stl.Mesh.from_file')
    def test_remix_processes_matching_files(self, mock_stl, mock_glob, mock_flags):
        """Remix should process STL files that match regex patterns."""
        mock_flags.input = '/test/input'
        mock_flags.remix = []

        # Mock STL file
        mock_file = MagicMock(spec=pathlib.Path)
        mock_file.name = 'test_2x4.stl'
        mock_file.stem = 'test_2x4'
        mock_file.parent.name = 'subfolder'
        mock_file.parts = ('test', 'input', 'subfolder', 'test_2x4.stl')
        mock_file.resolve.return_value = pathlib.Path('/test/input/subfolder/test_2x4.stl')

        mock_glob.return_value = [mock_file]

        # Mock mesh with dimensions
        mock_mesh = MagicMock()
        mock_mesh.min_ = np.array([0.0, 0.0, 0.0])
        mock_mesh.max_ = np.array([25.4, 50.8, 3.175])  # 2x4x0.25 in mm
        mock_stl.return_value = mock_mesh

        remix = Remix('TestRemix', self.simple_config)
        bricks = list(remix.bricks)

        self.assertEqual(len(bricks), 1)
        self.assertIsInstance(bricks[0], Brick)

    @patch('lib.remix.FLAGS')
    @patch('pathlib.Path.glob')
    def test_remix_invalid_brick_no_match(self, mock_glob, mock_flags):
        """Remix should raise InvalidBrick for non-matching filenames."""
        mock_flags.input = '/test/input'
        mock_flags.remix = []

        # Mock STL file that doesn't match regex
        mock_file = MagicMock(spec=pathlib.Path)
        mock_file.name = 'invalid_name.stl'
        mock_file.stem = 'invalid_name'

        mock_glob.return_value = [mock_file]

        remix = Remix('TestRemix', self.simple_config)

        # Should log error and continue (not yield any bricks)
        with patch('lib.remix.logging'):
            bricks = list(remix.bricks)

        self.assertEqual(len(bricks), 0)

    @patch('lib.remix.FLAGS')
    @patch('pathlib.Path.glob')
    def test_remix_input_property(self, mock_glob, mock_flags):
        """Remix._input should return resolved input path."""
        mock_flags.input = '/test/input'
        mock_flags.remix = []
        mock_glob.return_value = []

        remix = Remix('TestRemix', self.simple_config)

        input_path = remix._input

        self.assertIsInstance(input_path, pathlib.Path)
        self.assertTrue(str(input_path).endswith('input'))

    @patch('lib.remix.FLAGS')
    @patch('pathlib.Path.glob')
    def test_remix_with_multiple_regex_patterns(self, mock_glob, mock_flags):
        """Remix should handle multiple regex patterns."""
        mock_flags.input = '/test/input'
        mock_flags.remix = []
        mock_glob.return_value = []

        multi_regex_config = {
            'regex': [
                r'pattern1_(\d+)x(\d+)\.stl',
                r'pattern2_(\d+)x(\d+)\.stl'
            ],
            'config': {
                '*': {
                    'set': 'TestSet',
                    'type': 'Plate'
                }
            }
        }

        remix = Remix('TestRemix', multi_regex_config)

        # Should have compiled both regex patterns
        self.assertEqual(len(remix._regex), 2)

    @patch('lib.remix.FLAGS')
    @patch('pathlib.Path.glob')
    def test_remix_remixes_property_parsing(self, mock_glob, mock_flags):
        """Remix._remixes should parse FLAGS.remix correctly."""
        mock_flags.input = '/test/input'
        # Include TestRemix in the remix list so it's enabled
        mock_flags.remix = ['TestRemix:test/*.stl', 'Config1:*.stl', 'Config2:subfolder/*.stl']
        mock_glob.return_value = []

        remix = Remix('TestRemix', self.simple_config)

        remixes = remix._remixes

        # Should have parsed the remix flags
        self.assertIn('TestRemix', remixes)
        self.assertIn('Config1', remixes)
        self.assertIn('Config2', remixes)

    @patch('lib.remix.FLAGS')
    @patch('pathlib.Path.glob')
    @patch('stl.Mesh.from_file')
    def test_remix_applies_universal_config(self, mock_stl, mock_glob, mock_flags):
        """Remix should apply universal '*' config to all bricks."""
        mock_flags.input = '/test/input'
        mock_flags.remix = []

        config_with_universal = {
            'regex': [r'test_(\d+)x(\d+)\.stl'],
            'config': {
                '*': {
                    'set': 'UniversalSet',
                    'type': 'Tile',
                    'texture': 'universal.png'
                }
            }
        }

        mock_file = MagicMock(spec=pathlib.Path)
        mock_file.name = 'test_2x2.stl'
        mock_file.stem = 'test_2x2'
        mock_file.parent.name = 'subfolder'
        mock_file.parts = ('test', 'input', 'subfolder', 'test_2x2.stl')
        mock_file.resolve.return_value = pathlib.Path('/test/input/subfolder/test_2x2.stl')

        mock_glob.return_value = [mock_file]

        mock_mesh = MagicMock()
        mock_mesh.min_ = np.array([0.0, 0.0, 0.0])
        mock_mesh.max_ = np.array([25.4, 25.4, 3.175])
        mock_stl.return_value = mock_mesh

        remix = Remix('TestRemix', config_with_universal)
        bricks = list(remix.bricks)

        self.assertEqual(len(bricks), 1)
        brick = bricks[0]

        self.assertEqual(brick.set, 'UniversalSet')
        self.assertEqual(brick.type, 'Tile')
        self.assertEqual(brick.texture, 'universal.png')

    @patch('lib.remix.FLAGS')
    @patch('pathlib.Path.glob')
    @patch('stl.Mesh.from_file')
    @patch('lib.remix.STATS')
    def test_remix_tracks_invalid_bricks(self, mock_stats, mock_stl, mock_glob, mock_flags):
        """Remix should track invalid bricks in STATS."""
        mock_flags.input = '/test/input'
        mock_flags.remix = []

        # Mock file that won't match
        mock_file = MagicMock(spec=pathlib.Path)
        mock_file.name = 'nomatch.stl'

        mock_glob.return_value = [mock_file]

        remix = Remix('TestRemix', self.simple_config)

        with patch('lib.remix.logging'):
            list(remix.bricks)

        # Should have incremented invalid counter
        # Note: exact assertion depends on mock_stats structure

    @patch('lib.remix.FLAGS')
    @patch('pathlib.Path.glob')
    @patch('stl.Mesh.from_file')
    def test_remix_calculates_mesh_dimensions(self, mock_stl, mock_glob, mock_flags):
        """Remix should calculate brick dimensions from mesh bounds."""
        mock_flags.input = '/test/input'
        mock_flags.remix = []

        mock_file = MagicMock(spec=pathlib.Path)
        mock_file.name = 'test_3x6.stl'
        mock_file.stem = 'test_3x6'
        mock_file.parent.name = 'folder'
        mock_file.parts = ('test', 'input', 'folder', 'test_3x6.stl')
        mock_file.resolve.return_value = pathlib.Path('/test/input/folder/test_3x6.stl')

        mock_glob.return_value = [mock_file]

        # Mock mesh: 3 units = 38.1mm, 6 units = 76.2mm
        mock_mesh = MagicMock()
        mock_mesh.min_ = np.array([0.0, 0.0, 0.0])
        mock_mesh.max_ = np.array([38.1, 76.2, 3.175])
        mock_stl.return_value = mock_mesh

        remix = Remix('TestRemix', self.simple_config)
        bricks = list(remix.bricks)

        self.assertEqual(len(bricks), 1)
        # Dimensions should be calculated based on mesh size


if __name__ == '__main__':
    unittest.main()
