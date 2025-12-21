```
"""
Integration tests for the brick configuration system.

These tests run the actual configure.py script and verify the
generated OpenSCAD file output. They are slower than unit tests
and require file I/O.
"""

import unittest
import tempfile
import pathlib
import subprocess
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))


class TestIntegration(unittest.TestCase):
    """Integration tests for the configure.py script."""

    def test_generate_2x2_wood_planks_tile(self):
        """Should generate a 2x2 tile with wood_planks texture."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Directory to store generated files
            output_dir = pathlib.Path(tmpdir) / "output"
            output_dir.mkdir()

            # Path to the configuration file we'll create
            config_path = pathlib.Path(tmpdir) / "config.yaml"

            # YAML configuration for a 2x2 wood plank tile
            yaml_config = """
generate:
  MyTestTile:
    generate:
      x: [2]
      y: [2]
    config:
      type: Tile
      set: MyTest
      texture: wood_planks
"""
            # Write the configuration to a file
            with open(config_path, "w") as f:
                f.write(yaml_config)

            # Path to the configure.py script
            configure_script = str(pathlib.Path(__file__).parent.parent / "configure.py")

            # Run the configure script
            # We need to specify the config file and output directory
            cmd = [
                "python3",
                configure_script,
                "--config", str(config_path),
                "--output", str(output_dir)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)

            # Check that the script ran successfully
            self.assertEqual(result.returncode, 0, f"Configure script failed:\n{result.stderr}")

            # Check that the output file was created
            expected_file = output_dir / "MyTest" / "Tiles" / "MyTest-Tile-2x2.scad"
            self.assertTrue(expected_file.exists(), f"Expected output file not found: {expected_file}")

            # Check the contents of the generated file
            with open(expected_file, "r") as f:
                content = f.read()

            # Check for key parameters in the generated file
            self.assertIn('include <../../../../scad/brick.scad>', content)
            self.assertIn('x=2;', content)
            self.assertIn('y=2;', content)
            self.assertIn('texture="wood_planks";', content)


if __name__ == '__main__':
    unittest.main()

```