# Copilot Instructions

## Architecture Snapshot
- Python tooling now lives under `bin.DEPRECATED/`: CLI entrypoint [`bin.DEPRECATED/configure.py`](bin.DEPRECATED/configure.py) wires Abseil flags, loads YAML from `configs/*.yaml`, and delegates to [`lib/bricks.py`](bin.DEPRECATED/lib/bricks.py).
- Core domains split into: `Brick` model ([`lib/brick.py`](bin.DEPRECATED/lib/brick.py)), parametric `Generate` sets ([`lib/generate.py`](bin.DEPRECATED/lib/generate.py)), STL-driven `Remix` sets ([`lib/remix.py`](bin.DEPRECATED/lib/remix.py)), and shared constants/stats ([`lib/globals.py`](bin.DEPRECATED/lib/globals.py), [`lib/stats.py`](bin.DEPRECATED/lib/stats.py)). These modules remain authoritative even though the new `bin/` directory now only hosts the Abseil `reference.py` wrapper that shells out to `bin.DEPRECATED/configure.py`.
- `Bricks.writeConfigs()` formats `scad/brick.template.scad`, writes JSON parameter sets, drops Makefiles pointing to [`Makefile.mk`](Makefile.mk), and skips overwriting unless `--force` or params changed.
- Output tree mirrors brick metadata: each `Brick.path` (defaults `<Set>/<Type>s`) receives a `.scad` file plus generated `Makefile`/`config.json` for downstream OpenSCAD renders.

## Configuration Patterns
- YAML structure (see [`configs/Blanks.yaml`](configs/Blanks.yaml)): top-level `generate` / `remix` keys, each containing named blocks. `generate` blocks define `generate` (ranges), optional `condition` string (evaluated after `.format_map(conf)`), and base `config` merged into each brick.
- `Generate.bricks` cartesian-products declared iterables; guard invalid combos via conditions like `'{x} >= {y}'` to avoid duplicates.
- `Remix` requires `--input` plus optional `--remix name:glob`. Regex capture groups and filesystem parts feed templated config keys; string values run through `.format(**vars)` so `{meshDimension[0]}` patterns resolve.
- Textures reference `textures/textures.json`; `Brick.scadConfigItems()` auto-resolves names to `../textures/<file>.png`. Prefer adding metadata there instead of hardcoding paths.

## Build & Render Workflow
- Typical flow (see [README.md](README.md)): run `python3 bin.DEPRECATED/configure.py --config=configs/Blanks.yaml --output=/path/to/build` (or call [`bin/reference.py`](bin/reference.py) which wraps it) to materialize `.scad`, then from that directory run `make` (or `make -j4`) to invoke OpenSCAD for `.stl` generation.
- Root [Makefile](Makefile) exports `OPENSCADPATH=scad: textures`, regenerates config via `make configure`, and compiles `.scad` → `.stl` with `openscad --backend Manifold --export-format binstl`.
- Generated output subtrees rely on `Makefile.mk` for shared targets; keep it backward compatible when editing rules so previously emitted trees continue working.

## Testing & Tooling
- Primary regression coverage now lives under [`tests/`](tests/README.md) and runs with `pytest`. `make test`, `make test-verbose`, `make test-quiet`, and `make test-coverage` all invoke `pytest` on that directory, with the integration test spawning [`bin/reference.py`](bin/reference.py) to ensure the generated `output/` tree matches expectations. Legacy unit tests for the deprecated CLI still sit in [bin.DEPRECATED/tests/README.md](bin.DEPRECATED/tests/README.md) should deeper coverage ever be needed.
- Tests expect STATS logging to remain suppressed during `unittest` runs; honor the guard in `configure.main()` when touching logging.
- Mock STL interactions use `numpy-stl`; avoid importing OpenSCAD or file I/O in new logic without injecting seams for mocking.

## Conventions & Gotchas
- Abseil flags are defined across modules; keep definitions at import time (before flag parsing) and register validators like the `--output` directory check.
- `Bricks.add_brickset()` enforces unique names—new configs should use descriptive keys to prevent collisions.
- When extending YAML schemas, remember `ruamel.yaml` preserves order/comments; prefer `mergedeep`-style `<<: *Reference` anchors already common in configs.
- `Brick.scadConfigItems()` stringifies booleans to `true/false` for OpenSCAD. Always feed Python primitives; avoid pre-stringifying values in configs.
- Stats (`STATS[brick.set]['new'|'updated'|'unchanged'|'invalid']`) drive CLI summaries. Update counters whenever bypassing `writeConfigs()` default paths.

## External Dependencies
- Runtime Python deps: `absl-py`, `ruamel.yaml`, `regex`, `mergedeep`, `numpy`, `numpy-stl`. OpenSCAD must be on PATH with Manifold backend support.
- Environment expects `$OPENSCADPATH` to include `scad/` and `textures/`; root Makefile handles export but custom scripts need to mirror it.

## When Modifying or Adding Features
- Prefer augmenting YAML configs over hardcoding new bricks; tests cover `Generate`/`Remix` logic heavily.
- Keep new modules under `bin.DEPRECATED/lib/` and add targeted tests plus `make test-<module>` support if needed.
- Document new workflows beside existing guides ([MAKEFILE_TARGETS.md](MAKEFILE_TARGETS.md), [TESTING_QUICK_REF.md](TESTING_QUICK_REF.md), [TEST_INTEGRATION_SUMMARY.md](TEST_INTEGRATION_SUMMARY.md)) to maintain parity between automation and docs.
