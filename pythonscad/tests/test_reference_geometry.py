"""End-to-end geometry test for the PythonSCAD reference wall."""

import os
import pathlib
import shutil
import subprocess

import pytest

from pythonscad.tests import stl_compare

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
TESTDATA_DIR = PROJECT_ROOT / "pythonscad/tests/testdata"
REFERENCE_SCRIPT = PROJECT_ROOT / "pythonscad/reference.py"
REFERENCE_STL = TESTDATA_DIR / "Blank-Wall-4x1.stl"
PYTHONSCAD_EXE = os.environ.get("PYTHONSCAD", "pythonscad")
PYTHONSCAD_AVAILABLE = shutil.which(PYTHONSCAD_EXE) is not None
REFERENCE_TRIANGLE_COUNT = len(stl_compare.triangles_from_stl_bytes(REFERENCE_STL.read_bytes()))


def _run_pythonscad(args: list[str]) -> subprocess.CompletedProcess[bytes]:
    """Execute pythonscad with the requested script arguments."""

    command = [PYTHONSCAD_EXE, "--trust-python", "--export-format", "binstl", "-o", "-"] + args
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

@pytest.mark.skipif(not PYTHONSCAD_AVAILABLE, reason="pythonscad executable not found in PATH")
def test_reference_wall_stdout_matches_reference() -> None:
    result = _run_pythonscad([str(REFERENCE_SCRIPT)])
    stderr_text = result.stderr.decode("utf-8", errors="ignore")

    assert result.returncode == 0, f"pythonscad failed (code {result.returncode}): {stderr_text}"
    assert result.stdout, "pythonscad emitted no STL data on stdout"

    stl_compare.assert_stl_bytes_match_file(result.stdout, REFERENCE_STL, decimals=3)
    triangles = stl_compare.triangles_from_stl_bytes(result.stdout)
    assert len(triangles) == REFERENCE_TRIANGLE_COUNT, "Triangle count invariant changed; update reference data if intentional"
