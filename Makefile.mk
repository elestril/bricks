rwildcard=$(foreach d,$(wildcard $(1:=/*)),$(call rwildcard,$d,$2) $(filter $(subst *,%,$2),$d))

export OPENSCADPATH := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/scad)
SCAD_FILES := $(wildcard $(OPENSCADPATH)/*.scad)

STL := $(patsubst %.scad,%.stl,$(call rwildcard,*,*.scad))

TOPTARGETS := all stl clean distclean test test-verbose test-quiet test-coverage

all: $(STL)

.PHONY: clean distclean test test-verbose test-quiet test-coverage
clean:
	rm -f $(STL)

distclean: clean
	rm -rf *

# Test targets
test:
	@echo "Running tests..."
	python3 bin/tests/run_tests.py

test-verbose:
	@echo "Running tests with verbose output..."
	python3 bin/tests/run_tests.py -v

test-quiet:
	@echo "Running tests in quiet mode..."
	python3 bin/tests/run_tests.py -q

test-coverage:
	@echo "Running tests with coverage..."
	python3 -m coverage run -m unittest discover -s bin/tests -p "test_*.py"
	python3 -m coverage report
	@echo "HTML coverage report: htmlcov/index.html"
	python3 -m coverage html

%.stl: %.scad $(SCAD_FILES)
	@echo Generating $@
	-openscad --backend Manifold --export-format binstl -o $@ $<