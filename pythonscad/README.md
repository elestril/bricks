# PythonSCAD Toolkit

This directory hosts the Python-first tooling that mirrors the legacy OpenSCAD workflow.

- `reference.py` rebuilds the canonical `Blank-Wall-4x1` geometry directly in PythonSCAD. Run `pythonscad reference.py --output <path>` to emit an STL into the checked-in `Reference/` tree or a custom directory.
- `bricks/` contains reusable primitives (for example `stud.py`) that match the original SCAD modules and can be imported by new generators.
- `tests/` provides the pytest suite plus helpers for validating PythonSCAD output against the reference STLs. The `tests/testdata/` subtree holds immutable copies of the reference meshes used during assertions.

## Running the PythonSCAD Tests

From the repository root:

```
pytest pythonscad/tests
```

Or run inside the directory:

```
cd pythonscad/tests && pytest
```

The `conftest.py` in this folder automatically prepends the project root to `PYTHONPATH`, so imports work from either location. Pass any additional pytest flags as usual (for example `pytest -k reference -vv`).

Set the `PYTHONSCAD` environment variable if the executable lives outside your `PATH`. The tests also rely on `numpy-stl` for mesh comparison, so install that package in whichever Python environment drives pytest.

## Referencing OpenSCAD Assets

The PythonSCAD modules expect OpenSCAD primitives (such as `cube` or `rotate_extrude`) to be importable. Ensure `pythonscad` is installed and that the `openscad` Python bindings are on the active interpreter path when creating new generators.
