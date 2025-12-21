# PythonSCAD Tests

This folder hosts the pytest suite plus shared helpers for validating PythonSCAD output.

- `conftest.py` adds the repository root to `PYTHONPATH` so imports work whether pytest is launched from the repo root or this directory.
- `stl_compare.py` implements STL parsing and comparison utilities powered by `numpy-stl`. Install that dependency in whichever Python environment runs pytest. The helpers hash triangles after rounding so tiny numeric differences are tolerated.
- `test_reference_geometry.py` invokes `bin/reference.py`, ensures the requested bricks are generated into a temporary output directory, and validates that the resulting `config.json` contains the expected number of parameter sets. It also uses `stl_compare` to assert that the STL snapshot in `testdata/` matches the authoritative mesh under `Reference/` so fixtures stay in sync.

## Common Commands

```
pytest tests            # run all PythonSCAD tests from repo root
cd tests && pytest -k reference -vv
```

Set `PYTHONSCAD=/path/to/pythonscad` if the executable is not already on `PATH`. The generator script relies on `python3`, while `numpy-stl` must be available in the active environment to keep the STL comparison helper working.

The `testdata/` directory stores read-only STL fixtures mirrored from `Reference/`. Keep these files in sync whenever the upstream geometry intentionally changes.
