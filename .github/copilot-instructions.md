# Copilot Instructions

## Architecture Snapshot
- Modern tooling lives under `bricks/`: [`bricks/config.py`](bricks/config.py) reads YAML configs, expands `generate` blocks, and writes STL placeholders plus `config.json` metadata. [`bin/reference.py`](bin/reference.py) is the Abseil entrypoint that wires `--config/--output` flags to `bricks.config.build_from_yaml`.
- The legacy OpenSCAD pipeline still resides in `bin.DEPRECATED/` (see [`bin.DEPRECATED/configure.py`](bin.DEPRECATED/configure.py) and its `lib/` helpers) for archival compatibility, but the pytest suite and default workflows no longer invoke it.
- Generated trees now contain `.stl` files only. The new builder emits axis-aligned box meshes sized from the YAML parameters plus a `config.json` summary (`fileFormatVersion = 1`).
- Historical `.scad` templates, Makefile fragments, and related stats live exclusively in `bin.DEPRECATED/lib/` and should be touched only when explicitly working on the legacy flow.

## Configuration Patterns
- YAML structure (see [`configs/Blanks.yaml`](configs/Blanks.yaml)): top-level `generate` / `remix` keys, each containing named blocks. `generate` blocks define `generate` (ranges), optional `condition` string (evaluated after `.format_map(conf)`), and base `config` merged into each brick.
- `Generate.bricks` cartesian-products declared iterables; guard invalid combos via conditions like `'{x} >= {y}'` to avoid duplicates.
- `Remix` requires `--input` plus optional `--remix name:glob`. Regex capture groups and filesystem parts feed templated config keys; string values run through `.format(**vars)` so `{meshDimension[0]}` patterns resolve.
- Textures reference `textures/textures.json`; `Brick.scadConfigItems()` auto-resolves names to `../textures/<file>.png`. Prefer adding metadata there instead of hardcoding paths.

## Build & Render Workflow
- Modern flow (see [README.md](README.md)): run `python3 bin/reference.py --config=configs/Blanks.yaml --output=/tmp/output` to emit STL files directly. The script logs progress and never shells out to OpenSCAD.
- Legacy flow (still documented for completeness): `python3 bin.DEPRECATED/configure.py --config=configs/Blanks.yaml --output=...` will recreate `.scad` trees plus per-directory Makefiles pointing to [Makefile.mk](Makefile.mk), after which `make -j4` invokes OpenSCAD. Only touch this when you explicitly need the historical artifacts.
- Root [Makefile](Makefile) and [Makefile.mk](Makefile.mk) continue to describe the OpenSCAD toolchain; avoid removing targets unless you plan to migrate generated trees and downstream consumers simultaneously.

## Testing & Tooling
- Regression coverage lives under [`tests/`](tests/README.md) and runs with `pytest`. `make test*` targets all execute `pytest tests`, whose integration case runs `bin/reference.py` against `configs/Blanks.yaml` and asserts that 76 STL files plus `config.json` appear in a temp directory.
- Legacy unit tests for the deprecated CLI remain under [bin.DEPRECATED/tests/README.md](bin.DEPRECATED/tests/README.md); run them only when touching `_DEPRECATED` code.
- `tests/stl_compare.py` depends on `numpy-stl`. Keep `pip install numpy-stl` (or equivalent) documented wherever you add new STL assertions.

## Conventions & Gotchas
- Abseil flags should be declared at import time. `bin/reference.py` currently exposes `--config` and `--output`; new entrypoints should follow the same pattern so `pytest` can shell out predictably.
- `bricks/config.py` expects YAML files shaped like [`configs/Blanks.yaml`](configs/Blanks.yaml): each block contains `config`, optional `condition`, and an optional `generate` dict describing cartesian axes. Keep expressions simple (they're evaluated with `eval` after string formatting), and prefer descriptive block names to avoid collisions in output names.
- The STL writer purposely emits simple rectangular prisms sized from the `x/y/z` units. If you add richer geometry, keep the writer deterministic so fixture comparisons remain meaningful.
- When extending configs, prefer editing YAML over hardcoding Python values. The builder sanitizes merged dictionaries before serializing them into `config.json`.
- Anything under `bin.DEPRECATED/` is frozen unless you are intentionally maintaining the old OpenSCAD system.

## External Dependencies
- Runtime deps for the modern path: `absl-py`, `ruamel.yaml`, `numpy-stl` (tests only). No OpenSCAD binary is required for `bin/reference.py` or the pytest suite.
- Legacy flow additionally depends on `regex`, `mergedeep`, OpenSCAD, and the historical SCAD assets in `scad/` and `textures/`.

## When Modifying or Adding Features
- Start with YAML: new brick families or variants should be expressed in `configs/*.yaml`, then exercised through `bricks/config.py` so both the generator and pytest continue to agree on expected counts.
- If you need richer geometry, extend `bricks/config.py` (or add new helpers under `bricks/`) rather than reanimating the deprecated OpenSCAD stack. Keep emitted STL names/path conventions stable—the tests assert on both.
- When touching the legacy code, add/adjust tests under `bin.DEPRECATED/tests/` and clearly document the rationale since that path is in maintenance mode only.
- Continue updating the docs ([MAKEFILE_TARGETS.md](MAKEFILE_TARGETS.md), [TESTING_QUICK_REF.md](TESTING_QUICK_REF.md), [TEST_INTEGRATION_SUMMARY.md](TEST_INTEGRATION_SUMMARY.md)) whenever flows change so downstream users know whether to call `bin/reference.py` or the deprecated toolchain.
