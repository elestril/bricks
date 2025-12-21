#!/usr/bin/env python3
"""Generate the Blank brick set defined in configs/Blanks.yaml."""

import subprocess
import sys
from pathlib import Path

from absl import app, flags, logging

PROJECT_ROOT = Path(__file__).resolve().parents[1]

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
    output_dir.mkdir(parents=True, exist_ok=True)

    configure_script = PROJECT_ROOT / "bin.DEPRECATED" / "configure.py"
    if not configure_script.exists():
        raise FileNotFoundError(f"Could not locate configure.py at {configure_script}")

    command = [
        sys.executable,
        str(configure_script),
        f"--configs={config_path}",
        f"--output={output_dir}",
    ]
    logging.info("Generating bricks from %s into %s", config_path, output_dir)
    result = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    app.run(main)
