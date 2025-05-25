all: configs stl

include Makefile.mk

configs: configs.json


STL_FILES = $(shell [ -f configs.json ] && jq -r '.["parameterSets"].[].stl' < configs.json)

stl: configs $(STL_FILES)

$(STL_FILES): configs.json
	@mkdir -p $(dir $@)
	openscad --backend Manifold -p configs.json -P $(basename $(notdir $@)) -o $@ $(SCAD_DIR)/bricks.scad

clean:
	rm -f $(wildcard *.json **/*.stl)
