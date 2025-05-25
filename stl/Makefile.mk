SCAD_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))../scad)
SCAD_FILES := $(wildcard $(SCAD_DIR)/*.scad)

%.json: %.jsonnet
	jsonnet -o $@ $<

$(SUBDIRS): 
	$(MAKE) -C $@ $(MAKECMDGOALS)

%.stl: %.json
	openscad --backend Manifold -p $< -P $(basename $(notdir $@)) -o $@ $(SCAD_DIR)/bricks.scad