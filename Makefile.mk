rwildcard=$(foreach d,$(wildcard $(1:=/*)),$(call rwildcard,$d,$2) $(filter $(subst *,%,$2),$d))

# Get the base directory (parent of parent of this Makefile)
BASEDIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

# Set up OpenSCAD paths (scad library and textures)
export OPENSCADPATH := $(BASEDIR)/scad:$(BASEDIR)/textures
SCAD_FILES := $(wildcard $(BASEDIR)/scad/*.scad)

STL := $(patsubst %.scad,%.stl,$(call rwildcard,*,*.scad))

TOPTARGETS := all stl clean distclean test test-verbose test-quiet test-coverage preview

all: $(STL)

.PHONY: clean distclean test test-verbose test-quiet test-coverage preview
clean:
	rm -f $(STL)

distclean: clean
	rm -rf *

# Test targets
test:
	@echo "Running tests..."
	python3 bin.DEPRECATED/tests/run_tests.py

test-verbose:
	@echo "Running tests with verbose output..."
	python3 bin.DEPRECATED/tests/run_tests.py -v

test-quiet:
	@echo "Running tests in quiet mode..."
	python3 bin.DEPRECATED/tests/run_tests.py -q

test-coverage:
	@echo "Running tests with coverage..."
	python3 -m coverage run -m unittest discover -s bin.DEPRECATED/tests -p "test_*.py"
	python3 -m coverage report
	@echo "HTML coverage report: htmlcov/index.html"
	python3 -m coverage html

# Preview target - open OpenSCAD in interactive mode
# Usage: make preview FILE=relative/path/to/file.scad
preview:
	@if [ -z "$(FILE)" ]; then \
		echo "Error: FILE parameter required"; \
		echo "Usage: make preview FILE=path/to/file.scad"; \
		echo "Example: make preview FILE=Tiles/RusticWood-Tile-2x2.scad"; \
		exit 1; \
	fi
	@if [ ! -f "$(FILE)" ]; then \
		echo "Error: File '$(FILE)' not found"; \
		exit 1; \
	fi
	@echo "Opening $(FILE) in OpenSCAD..."
	@echo "OPENSCADPATH=$(OPENSCADPATH)"
	openscad $(FILE)

%.stl: %.scad $(SCAD_FILES)
	@echo Generating $@
	-openscad --backend Manifold --export-format binstl -o $@ $<