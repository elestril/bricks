# Root Makefile for brick configuration system

SUBDIRS := $(wildcard */)

# Set up OpenSCAD paths (scad library and textures)
export OPENSCADPATH := $(abspath scad):$(abspath textures)

.PHONY: all clean test test-verbose test-quiet test-coverage help preview configure stl

# Find all generated .scad files (excluding BOSL2 and bin directories)
SCAD_FILES := $(shell find . -name "*.scad" -not -path "./BOSL2/*" -not -path "./scad/*" -not -path "./bin/*" 2>/dev/null)
STL_FILES := $(SCAD_FILES:.scad=.stl)

# SCAD library dependencies (all STL files depend on these)
SCAD_LIB := $(wildcard scad/*.scad)

# Default target - configure and build all STL files
all: stl

# Build all STL files (parallel-safe)
stl: configure $(STL_FILES)

# Pattern rule for building STL files from SCAD files
# This allows Make to build multiple STL files in parallel with -j
%.stl: %.scad $(SCAD_LIB)
	@echo "Generating $@"
	@openscad --backend Manifold --export-format binstl -o $@ $< 2>/dev/null || (echo "Failed: $@" && false)

# Run the configuration script to generate OpenSCAD files
# Usage: make configure [OUTPUT=path/to/output]
configure:
	@echo "Configuring bricks from YAML files..."
	@if [ -n "$(OUTPUT)" ]; then \
		echo "Output directory: $(OUTPUT)"; \
		python3 bin/configure.py --output=$(OUTPUT); \
	else \
		python3 bin/configure.py; \
	fi

# Test targets
test:
	@echo "Running all tests..."
	@python3 bin/tests/run_tests.py

test-verbose:
	@echo "Running tests with verbose output..."
	@python3 bin/tests/run_tests.py -v

test-quiet:
	@echo "Running tests in quiet mode..."
	@python3 bin/tests/run_tests.py -q

test-coverage:
	@echo "Running tests with coverage..."
	@python3 -m coverage run -m unittest discover -s bin/tests -p "test_*.py"
	@python3 -m coverage report
	@echo ""
	@echo "HTML coverage report generated: htmlcov/index.html"
	@python3 -m coverage html

# Run specific test module
test-%:
	@echo "Running tests for $*..."
	@python3 bin/tests/run_tests.py test_$*

# Clean targets
clean:
	@echo "Cleaning generated files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf htmlcov/ .coverage

# Preview target - open OpenSCAD in interactive mode
# Usage: make preview FILE=path/to/file.scad
preview:
	@if [ -z "$(FILE)" ]; then \
		echo "Error: FILE parameter required"; \
		echo "Usage: make preview FILE=path/to/file.scad"; \
		echo "Example: make preview FILE=RusticWood/Tiles/RusticWood-Tile-2x2.scad"; \
		exit 1; \
	fi
	@if [ ! -f "$(FILE)" ]; then \
		echo "Error: File '$(FILE)' not found"; \
		exit 1; \
	fi
	@echo "Opening $(FILE) in OpenSCAD..."
	@echo "OPENSCADPATH=$(OPENSCADPATH)"
	openscad $(FILE)

# Help target
help:
	@echo "Brick Configuration System - Makefile targets"
	@echo ""
	@echo "Main targets:"
	@echo "  make                 - Generate OpenSCAD files and build all STL files (default)"
	@echo "  make all             - Same as 'make'"
	@echo "  make stl             - Build all STL files from .scad files"
	@echo "  make configure       - Generate OpenSCAD files from YAML configs only"
	@echo "  make -j<N>           - Build STL files in parallel with N jobs"
	@echo "                         Example: make -j8 (use 8 parallel jobs)"
	@echo ""
	@echo "Configuration options:"
	@echo "  OUTPUT=path          - Specify output directory (default: current dir)"
	@echo "                         Example: make configure OUTPUT=/tmp/output"
	@echo ""
	@echo "Preview targets:"
	@echo "  make preview FILE=<file.scad>  - Open .scad file in OpenSCAD GUI"
	@echo "                         Example: make preview FILE=RusticWood/Tiles/RusticWood-Tile-2x2.scad"
	@echo ""
	@echo "Test targets:"
	@echo "  make test            - Run all tests"
	@echo "  make test-verbose    - Run tests with verbose output"
	@echo "  make test-quiet      - Run tests in quiet mode"
	@echo "  make test-coverage   - Run tests with coverage report"
	@echo "  make test-<module>   - Run specific test module (e.g., make test-brick)"
	@echo ""
	@echo "Clean targets:"
	@echo "  make clean           - Remove generated Python cache files and coverage reports"
	@echo ""
	@echo "Examples:"
	@echo "  make configure OUTPUT=/tmp/bricks  - Generate to /tmp/bricks"
	@echo "  make preview FILE=Blank/Tiles/Blank-Tile-4x4.scad  - Preview a brick"
	@echo "  make test-brick      - Run brick.py tests"
	@echo "  make test-generate   - Run generate.py tests"
	@echo "  make test-remix      - Run remix.py tests"

.PHONY: $(TOPTARGETS) $(SUBDIRS) stl