# Testing Quick Reference Card

## 🚀 Quick Start

```bash
make test              # Run all 92 tests (clean output!)
make test-brick        # Run specific module
make test-verbose      # Debug test failures
make test-coverage     # Check code coverage
make help              # See all targets
```

## 📊 Test Targets

| Command | Tests | Purpose |
|---------|-------|---------|
| `make test` | 92 | Normal output |
| `make test-verbose` | 92 | Detailed output |
| `make test-quiet` | 92 | Clean minimal output |
| `make test-coverage` | 92 | With coverage report |

## 🎯 Module-Specific Tests

| Command | Tests | Module |
|---------|-------|--------|
| `make test-globals` | 6 | Global constants |
| `make test-stats` | 8 | Statistics |
| `make test-brick` | 39 | Brick class |
| `make test-generate` | 14 | Generation |
| `make test-remix` | 12 | STL remix |
| `make test-bricks` | 10 | Orchestration |
| `make test-configure` | 13 | Main script |

## 🧹 Maintenance

```bash
make clean             # Remove cache/coverage files
make clean test        # Clean then test
```

## 📝 Manual Testing

```bash
# Using test runner directly
python3 bin/tests/run_tests.py              # All tests
python3 bin/tests/run_tests.py -v           # Verbose
python3 bin/tests/run_tests.py test_brick   # Specific

# Using unittest
python3 -m unittest discover -s bin/tests   # All tests
python3 -m unittest bin.tests.test_brick    # Module
```

## ✅ Current Status

- **Total Tests:** 92
- **Status:** ✅ ALL PASSING
- **Runtime:** ~0.03 seconds
- **Coverage:** All modules
- **Output:** Clean (no STATS pollution)

## 📚 Documentation

- [MAKEFILE_TARGETS.md](MAKEFILE_TARGETS.md) - Complete target reference
- [bin/tests/README.md](bin/tests/README.md) - Test suite guide
- [TEST_INTEGRATION_SUMMARY.md](TEST_INTEGRATION_SUMMARY.md) - Full summary

## 🔧 Common Workflows

**Before committing:**
```bash
make clean test
```

**During development:**
```bash
# Make changes to brick.py...
make test-brick
```

**Before release:**
```bash
make test-coverage
open htmlcov/index.html
```

**CI/CD:**
```bash
make test-quiet  # Exit code 0 on success
```

---

*All 92 tests passing with clean output ✨*
