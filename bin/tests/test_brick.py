"""
Tests for lib.brick module.

Tests the Brick class which represents individual 3D printable bricks
with their configurations and parameters.
"""

import pathlib
import unittest
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from lib.brick import Brick, InvalidBrick


class TestInvalidBrick(unittest.TestCase):
    """Test cases for InvalidBrick exception."""

    def test_invalid_brick_is_value_error(self):
        """InvalidBrick should be a ValueError subclass."""
        self.assertTrue(issubclass(InvalidBrick, ValueError))

    def test_invalid_brick_can_be_raised(self):
        """InvalidBrick should be raisable with a message."""
        with self.assertRaises(InvalidBrick) as context:
            raise InvalidBrick("Test error message")

        self.assertIn("Test error message", str(context.exception))


class TestBrick(unittest.TestCase):
    """Test cases for the Brick class."""

    def test_brick_creation_with_defaults(self):
        """Brick should be created with default parameters."""
        brick = Brick(set='TestSet')

        self.assertEqual(brick.family, 'Square')
        self.assertEqual(brick.type, 'Plate')
        self.assertEqual(brick.set, 'TestSet')
        self.assertIsNone(brick.variant)

    def test_brick_plate_defaults(self):
        """Plate type should have correct default features."""
        brick = Brick(set='Test', type='Plate', x=2, y=4)

        self.assertTrue(brick.studs)
        self.assertTrue(brick.sockets)
        self.assertTrue(brick.grid)
        self.assertEqual(brick.size[2], 0.25)

    def test_brick_tile_defaults(self):
        """Tile type should have correct default features."""
        brick = Brick(set='Test', type='Tile', x=2, y=4)

        self.assertFalse(brick.studs)  # Tiles have smooth tops
        self.assertTrue(brick.sockets)
        self.assertTrue(brick.grid)
        self.assertEqual(brick.size[2], 0.25)

    def test_brick_wall_defaults(self):
        """Wall type should have correct default features."""
        brick = Brick(set='Test', type='Wall', x=4, y=1)

        self.assertTrue(brick.studs)
        self.assertTrue(brick.sockets)
        self.assertFalse(brick.grid)  # Walls don't have internal grids
        self.assertEqual(brick.size[2], 4.0)

    def test_brick_riser_defaults(self):
        """Riser type should have correct default features."""
        brick = Brick(set='Test', type='Riser', x=2, y=2)

        self.assertTrue(brick.studs)
        self.assertTrue(brick.sockets)
        self.assertTrue(brick.grid)
        self.assertEqual(brick.size[2], 1.0)

    def test_brick_size_from_parameters(self):
        """Brick size should be set from x, y, z parameters."""
        brick = Brick(set='Test', x=3, y=5, z=0.5)

        self.assertEqual(brick.size, [3, 5, 0.5])
        self.assertEqual(brick.x, 3)
        self.assertEqual(brick.y, 5)
        self.assertEqual(brick.z, 0.5)

    def test_brick_size_from_size_parameter(self):
        """Brick size can be set via size parameter."""
        brick = Brick(set='Test', size=[4, 6, 0.25])

        self.assertEqual(brick.size, [4, 6, 0.25])
        self.assertEqual(brick.x, 4)
        self.assertEqual(brick.y, 6)
        self.assertEqual(brick.z, 0.25)

    def test_brick_name_generation_square(self):
        """Brick name should be generated correctly for square bricks."""
        brick = Brick(set='MySet', type='Plate', x=2, y=4)

        expected_name = 'MySet-Plate-2x4'
        self.assertEqual(brick.name, expected_name)

    def test_brick_name_generation_with_variant(self):
        """Brick name should include variant when specified."""
        brick = Brick(set='MySet', type='Tile', x=2, y=2, variant='Special')

        expected_name = 'MySet-Tile-2x2-Special'
        self.assertEqual(brick.name, expected_name)

    def test_brick_name_generation_hex(self):
        """Brick name should format hex family correctly."""
        brick = Brick(set='Test', type='Tile', family='Hex', x=3, y=4)

        self.assertIn('Hex', brick.name)
        self.assertIn('3x4', brick.name)

    def test_brick_name_generation_hexr(self):
        """Brick name should format HexR family correctly."""
        brick = Brick(set='Test', type='Tile', family='HexR', x=2, y=0)

        self.assertIn('HexR2', brick.name)

    def test_brick_name_generation_hexs(self):
        """Brick name should format HexS family correctly."""
        brick = Brick(set='Test', type='Tile', family='HexS', x=3, y=0)

        self.assertIn('HexS3', brick.name)

    def test_brick_name_custom_override(self):
        """Brick name can be overridden via name parameter."""
        brick = Brick(set='Test', type='Plate', x=2, y=4, name='CustomName')

        self.assertEqual(brick.name, 'CustomName')

    def test_brick_path_default(self):
        """Brick path should default to set/type+s."""
        brick = Brick(set='MySet', type='Plate', x=2, y=4)

        expected_path = pathlib.Path('MySet/Plates')
        self.assertEqual(brick.path, expected_path)

    def test_brick_path_custom_override(self):
        """Brick path can be overridden via path parameter."""
        custom_path = pathlib.Path('Custom/Path')
        brick = Brick(set='Test', type='Tile', x=1, y=1, path=custom_path)

        self.assertEqual(brick.path, custom_path)

    def test_brick_texture_parameter(self):
        """Brick should accept and store texture parameter."""
        brick = Brick(set='Test', type='Tile', x=2, y=2, texture='rustic_wood.png')

        self.assertEqual(brick.texture, 'rustic_wood.png')

    def test_brick_rotation_parameter(self):
        """Brick should accept and store rotation parameter."""
        brick = Brick(set='Test', type='Plate', x=2, y=2, rot=[0, 90, 0])

        self.assertEqual(brick.rot, [0, 90, 0])

    def test_brick_input_stl_parameter(self):
        """Brick should accept input STL file parameter."""
        input_path = pathlib.Path('/path/to/model.stl')
        brick = Brick(set='Test', type='Plate', x=2, y=2, input=input_path)

        self.assertEqual(brick.input, input_path)

    def test_brick_cut_parameters(self):
        """Brick should accept cut plane parameters."""
        brick = Brick(set='Test', type='Tile', x=2, y=2, cutX=0, cutY=-1, cutZ=5)

        self.assertEqual(brick.cutX, 0)
        self.assertEqual(brick.cutY, -1)
        self.assertEqual(brick.cutZ, 5)

    def test_brick_scad_config_items(self):
        """scadConfigItems should return properly formatted dict."""
        brick = Brick(set='Test', type='Plate', x=2, y=4)

        config = brick.scadConfigItems()

        self.assertEqual(config['family'], 'Square')
        self.assertEqual(config['studs'], 'true')
        self.assertEqual(config['sockets'], 'true')
        self.assertEqual(config['grid'], 'true')
        self.assertEqual(config['size'], '[2, 4, 0.25]')

    def test_brick_scad_config_items_boolean_false(self):
        """scadConfigItems should format False booleans correctly."""
        brick = Brick(set='Test', type='Tile', x=2, y=2)

        config = brick.scadConfigItems()

        self.assertEqual(config['studs'], 'false')

    def test_brick_scad_config_items_undef_for_missing(self):
        """scadConfigItems should return 'undef' for missing keys."""
        brick = Brick(set='Test', type='Plate', x=2, y=2)

        config = brick.scadConfigItems()

        # Access a key that doesn't exist
        self.assertEqual(config['nonexistent_key'], 'undef')

    def test_brick_str_representation(self):
        """Brick __str__ should return its name."""
        brick = Brick(set='MySet', type='Plate', x=2, y=4)

        self.assertEqual(str(brick), 'MySet-Plate-2x4')

    def test_brick_custom_studs_override(self):
        """Brick should allow overriding default studs value."""
        # Plates normally have studs=True, but can be overridden
        brick = Brick(set='Test', type='Plate', x=2, y=2, studs=False)

        self.assertFalse(brick.studs)

    def test_brick_bottom_fill_parameter(self):
        """Brick should accept bottomFill parameter."""
        brick = Brick(set='Test', type='Plate', x=2, y=2, bottomFill=0.5)

        self.assertEqual(brick.bottomFill, 0.5)

    def test_brick_mirror_z_parameter(self):
        """Brick should accept mirrorZ parameter."""
        brick = Brick(set='Test', type='Plate', x=2, y=2, mirrorZ=1.5)

        self.assertEqual(brick.mirrorZ, 1.5)


if __name__ == '__main__':
    unittest.main()
