SCAD_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/scad)
SCAD_FILES := $(wildcard $(SCAD_DIR)/*.scad)

TOPTARGETS := all stl clean distclean

SUBDIRS := $(patsubst %/Makefile,%,$(wildcard */Makefile))

all: stl $(SUBDIRS)

stl: $(patsubst %.json,%.stl,$(wildcard *.json))

.PHONY: $(TOPTARGETS) $(SUBDIRS)
$(SUBDIRS):
	$(MAKE) -C $@ $(MAKECMDGOALS)

clean: $(SUBDIRS)
	rm -f $(wildcard *.stl)

distclean: clean
	rm -f $(wildcard *.json) Makefile

%.json: %.jsonnet
	jsonnet -o $@ $<

%.stl: %.json
	@echo Making $@
	@openscad --backend Manifold -p $< -P $(basename $(notdir $@)) --export-format binstl -o $@ $(SCAD_DIR)/bricks.scad 2> /dev/null