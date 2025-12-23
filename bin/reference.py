#!/usr/bin/env pythonscad
"""Generate STL bricks defined in a YAML configuration file."""

import sys
from pathlib import Path

from absl import app, flags, logging

from bricks import brick
from openscad import *

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))



FLAGS = flags.FLAGS
flags.DEFINE_string(
    "config",
    str(PROJECT_ROOT / "configs/Blanks.yaml"),
    "Path to the YAML configuration file describing the bricks to generate.",
)
flags.DEFINE_string(
    "output",
    str(PROJECT_ROOT / "output"),
    "Directory where the generated brick files will be written.",
)


def main(argv: list[str]) -> None:
    del argv  # Unused but required by absl.app

    config_path = Path(FLAGS.config).resolve()
    output_dir = Path(FLAGS.output).resolve()
    logging.info("Generating bricks from %s into %s", config_path, output_dir)

    b = brick.brick(brick.Point(2, 4, 1))
    b.show()

if __name__ == "__main__":
    print("WARNING: This script is deprecated. Use 'bricks build' command instead.")
    app.run(main)


print("FOO")