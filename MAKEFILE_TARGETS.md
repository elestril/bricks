# Makefile Targets Reference

This document describes all available Make targets for the brick configuration system.

## Quick Reference

```bash
make help              # Show all available targets
make test              # Run all tests
make test-brick        # Run specific test module
make test-coverage     # Run tests with coverage report
make clean             # Clean up generated files
```

## Main Targets

### `make` or `make all`
**Description:** Default target. Runs the configuration script to generate OpenSCAD files from YAML configs.

```bash
make
# or
make all
```

**What it does:**
- Executes `python3 bin/configure.py`
- Processes all YAML files in `configs/` directory
- Generates OpenSCAD `.scad` files
- Creates `config.json` with parameter sets
- Outputs statistics

### `make configure`
**Description:** Explicitly run the brick configuration script.

```bash
make configure
```

**Same as:** `make all`

## Test Targets

### `make test`
**Description:** Run all tests with normal output.

```bash
make test
```

**What it does:**
- Runs all 91 tests across 7 test modules
- Shows basic test progress
- Reports pass/fail status
- Exit code 0 on success, 1 on failure

**Output example:**
```
Running all tests...
...................................................................................
----------------------------------------------------------------------
Ran 91 tests in 0.028s

OK
```

### `make test-verbose`
**Description:** Run all tests with detailed verbose output.

```bash
make test-verbose
```

**What it does:**
- Runs all tests with `-v` flag
- Shows each test name and description
- Displays detailed results for each test
- Useful for debugging test failures

**Output example:**
```
Running tests with verbose output...
test_brick_creation_with_defaults (test_brick.TestBrick)
Brick should be created with default parameters. ... ok
test_brick_plate_defaults (test_brick.TestBrick)
Plate type should have correct default features. ... ok
...
```

### `make test-quiet`
**Description:** Run all tests with minimal output.

```bash
make test-quiet
```

**What it does:**
- Runs all tests with `-q` flag
- Shows only summary (no individual test progress)
- Displays only failures (if any)
- Fastest output for CI/CD

**Output example:**
```
Running tests in quiet mode...
----------------------------------------------------------------------
Ran 91 tests in 0.024s

OK
```

### `make test-coverage`
**Description:** Run all tests with code coverage analysis.

```bash
make test-coverage
```

**What it does:**
- Runs tests with Python coverage module
- Generates coverage statistics
- Creates HTML coverage report in `htmlcov/` directory
- Shows which lines of code are tested

**Output example:**
```
Running tests with coverage...
Name                      Stmts   Miss  Cover
---------------------------------------------
bin/lib/brick.py             85      5    94%
bin/lib/bricks.py           112     15    87%
bin/lib/generate.py          28      2    93%
bin/lib/globals.py           12      0   100%
bin/lib/remix.py             95     12    87%
bin/lib/stats.py              3      0   100%
bin/configure.py             18      2    89%
---------------------------------------------
TOTAL                       353     36    90%

HTML coverage report generated: htmlcov/index.html
```

**View HTML report:**
```bash
make test-coverage
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### `make test-<module>`
**Description:** Run tests for a specific module.

**Available modules:**
- `make test-globals` - Test global constants and utilities
- `make test-stats` - Test statistics tracking
- `make test-brick` - Test Brick class (39 tests)
- `make test-generate` - Test parametric generation (14 tests)
- `make test-remix` - Test STL remixing (12 tests)
- `make test-bricks` - Test main orchestration (10 tests)
- `make test-configure` - Test configuration script (12 tests)

**Examples:**
```bash
make test-brick        # Run only brick tests
make test-generate     # Run only generation tests
make test-remix        # Run only remix tests
```

**What it does:**
- Runs only the specified test module
- Useful for focused testing during development
- Faster than running all tests

## Clean Targets

### `make clean`
**Description:** Remove generated Python cache files and coverage reports.

```bash
make clean
```

**What it removes:**
- `*.pyc` files (compiled Python bytecode)
- `__pycache__/` directories
- `htmlcov/` directory (coverage HTML reports)
- `.coverage` file (coverage data)

**When to use:**
- Before committing code
- To reset test environment
- When coverage reports are outdated
- To free up disk space

## Help Target

### `make help`
**Description:** Display help information about all available targets.

```bash
make help
```

**What it shows:**
- List of all main targets
- List of all test targets
- List of clean targets
- Usage examples
- Quick reference guide

## Advanced Usage

### Running Tests in CI/CD

**GitHub Actions:**
```yaml
- name: Run Tests
  run: make test-quiet

- name: Generate Coverage Report
  run: make test-coverage
```

**GitLab CI:**
```yaml
test:
  script:
    - make test-quiet
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

### Combining Targets

```bash
# Clean, then test
make clean test

# Test with coverage, then view report
make test-coverage && open htmlcov/index.html

# Run specific tests multiple times
for i in {1..5}; do make test-brick; done
```

### Integration with Development Workflow

**Before committing:**
```bash
make clean
make test
```

**During development:**
```bash
# Make code changes...
make test-brick  # Test only what you changed

# More changes...
make test-verbose  # Debug test failures
```

**Before release:**
```bash
make clean
make test-coverage
# Review coverage report
# Ensure >80% coverage
```

## Test Statistics

| Target | Tests Run | Typical Duration | Output Level |
|--------|-----------|------------------|--------------|
| `make test` | 91 | ~0.03s | Normal |
| `make test-verbose` | 91 | ~0.03s | Verbose |
| `make test-quiet` | 91 | ~0.02s | Minimal |
| `make test-brick` | 39 | ~0.01s | Normal |
| `make test-generate` | 14 | ~0.01s | Normal |
| `make test-remix` | 12 | ~0.01s | Normal |

## Troubleshooting

### Tests Fail

```bash
# Run with verbose output to see details
make test-verbose

# Run specific failing test
make test-<module>
```

### Coverage Not Installed

```bash
pip3 install coverage
# or
python3 -m pip install coverage
```

### Python Not Found

The Makefiles use `python3` explicitly. If you need to use a different Python:

```bash
# Edit Makefile and change:
python3 bin/tests/run_tests.py
# to:
/path/to/your/python bin/tests/run_tests.py
```

### Permissions Issues

```bash
# Make test runner executable
chmod +x bin/tests/run_tests.py

# Run with explicit python
python3 bin/tests/run_tests.py
```

## Files Modified

The following Makefiles have been updated with test targets:

1. **[Makefile](Makefile)** - Root Makefile with all test targets
2. **[Makefile.mk](Makefile.mk)** - Shared Makefile included by output directories

Both files now support:
- `test` - Run all tests
- `test-verbose` - Verbose test output
- `test-quiet` - Quiet test output
- `test-coverage` - Coverage reports
- `test-<module>` - Specific module tests (root Makefile only)
- `help` - Show available targets (root Makefile only)

## Related Documentation

- [bin/tests/README.md](bin/tests/README.md) - Test suite documentation
- [bin/tests/TESTS_SUMMARY.md](bin/tests/TESTS_SUMMARY.md) - Detailed test breakdown
- Test runner: [bin/tests/run_tests.py](bin/tests/run_tests.py)
