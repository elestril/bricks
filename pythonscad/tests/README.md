# PythonSCAD Tests

This folder hosts the pytest suite plus shared helpers for validating PythonSCAD output.

- `conftest.py` adds the repository root to `PYTHONPATH` so imports work whether pytest is launched from the repo root or this directory.
- `stl_compare.py` implements STL parsing and comparison utilities powered by `numpy-stl`. Install that dependency in whichever Python environment runs pytest. The helpers hash triangles after rounding so tiny numeric differences are tolerated.
- `test_reference_geometry.py` runs `pythonscad` as a subprocess, streams the generated `Blank-Wall-4x1` STL through stdout, and compares it to the copy under `testdata/`. The test also enforces the triangle-count invariant (currently 1780 facets) to guard against accidental geometry changes.

## Common Commands

```
pytest pythonscad/tests            # run all PythonSCAD tests from repo root
cd pythonscad/tests && pytest -k reference -vv
```

Set `PYTHONSCAD=/path/to/pythonscad` if the executable is not already on `PATH`. The tests automatically skip when the binary is missing, which allows developers without OpenSCAD to run the rest of the suite.

The `testdata/` directory stores read-only STL fixtures mirrored from `Reference/`. Keep these files in sync whenever the upstream geometry intentionally changes.
