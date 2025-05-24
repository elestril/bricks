SCAD_DIR = $(abspath $(dir $(lastword $(MAKEFILE_LIST)))../scad)
SCAD_FILES = $(wildcard $(SCAD_DIR)/*.scad)

STL_FILES = $(shell [ -f configs.json ] && jq -r '.["parameterSets"].[].stl' < configs.json)

stl: $(STL_FILES)

%.stl: %.json
	openscad --backend Manifold -p $< -P $(basename $(notdir $@)) -o $@ $(SCAD_DIR)/bricks.scad

$(STL_FILES): configs.json
	@mkdir -p $(dir $@)
	openscad --backend Manifold -p configs.json -P $(basename $(notdir $@)) -o $@ $(SCAD_DIR)/bricks.scad

.PHONY: clean distclean
clean: 
	rm -f $(wildcard *.stl)

distclean: clean
	rm -f $(wildcard *.json)