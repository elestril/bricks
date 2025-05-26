SCAD_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/scad)
SCAD_FILES := $(wildcard $(SCAD_DIR)/*.scad)

TOPTARGETS := all stl

SUBDIRS := $(patsubst %/Makefile,%,$(wildcard */Makefile))

all: stl $(SUBDIRS)

stl: $(patsubst %.json,%.stl,$(wildcard *.json))

.PHONY: $(TOPTARGETS) $(SUBDIRS)
$(SUBDIRS):
	$(MAKE) -C $@ $(MAKECMDGOALS)

.PHONY: all $(SUBDIRS)

%.json: %.jsonnet
	jsonnet -o $@ $<

%.stl: %.json
	openscad --backend Manifold -p $< -P $(basename $(notdir $@)) -o $@ $(SCAD_DIR)/bricks.scad