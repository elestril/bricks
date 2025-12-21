"""Integration tests for the reference generation workflow."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

import stl_compare

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_SCRIPT = PROJECT_ROOT / "bin/reference.py"
CONFIG_PATH = PROJECT_ROOT / "configs/Blanks.yaml"
REFERENCE_STL = PROJECT_ROOT / "Reference/Walls/Blank-Wall-4x1.stl"
TESTDATA_STL = PROJECT_ROOT / "tests/testdata/Blank-Wall-4x1.stl"
EXPECTED_PARAMETER_SETS = 76
SAMPLE_BRICKS = [
    Path("Blank/Tiles/Blank-Tile-2x2.scad"),
    Path("Reference/Walls/Blank-Wall-4x1.scad"),
]


@pytest.fixture()
def generated_output(tmp_path: Path) -> Path:
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    command = [
        sys.executable,
        str(REFERENCE_SCRIPT),
        f"--config={CONFIG_PATH}",
        f"--output={output_dir}",
    ]
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)
    return output_dir


def test_reference_generates_blank_bricks(generated_output: Path) -> None:
    config_path = generated_output / "config.json"
    assert config_path.is_file(), "config.json missing from generated output"

    with config_path.open() as fp:
        parameters = json.load(fp).get("parameterSets", {})

    assert len(parameters) == EXPECTED_PARAMETER_SETS, "Unexpected brick count in generated config"

    for relative in SAMPLE_BRICKS:
        assert (generated_output / relative).is_file(), f"Missing generated brick: {relative}"


def test_reference_testdata_matches_source() -> None:
    test_copy = TESTDATA_STL.read_bytes()
    stl_compare.assert_stl_bytes_match_file(test_copy, REFERENCE_STL, decimals=3)
