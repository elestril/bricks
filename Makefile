# Root Makefile for brick configuration system

SUBDIRS := $(wildcard */)

.PHONY: all clean test test-verbose test-quiet test-coverage help

# Default target
all: configure

# Run the configuration script to generate OpenSCAD files
configure:
	@echo "Configuring bricks from YAML files..."
	python3 bin/configure.py

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

# Help target
help:
	@echo "Brick Configuration System - Makefile targets"
	@echo ""
	@echo "Main targets:"
	@echo "  make configure        - Generate OpenSCAD files from YAML configs"
	@echo "  make all             - Same as 'make configure'"
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
	@echo "  make test-brick      - Run brick.py tests"
	@echo "  make test-generate   - Run generate.py tests"
	@echo "  make test-remix      - Run remix.py tests"

.PHONY: $(TOPTARGETS) $(SUBDIRS) stl