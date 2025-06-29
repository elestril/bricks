rwildcard=$(foreach d,$(wildcard $(1:=/*)),$(call rwildcard,$d,$2) $(filter $(subst *,%,$2),$d))

export OPENSCADPATH := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/scad)
SCAD_FILES := $(wildcard $(OPENSCADPATH)/*.scad)

STL := $(patsubst %.scad,%.stl,$(call rwildcard,*,*.scad))

TOPTARGETS := all stl clean distclean

all: $(STL)

.PHONY: clean distclean
clean: 
	rm -f $(STL)

distclean: clean
	rm -rf *

%.stl: %.scad $(SCAD_FILES)
	@echo Generating $@
	@openscad --backend Manifold --export-format binstl -o $@ $< 2>/dev/null