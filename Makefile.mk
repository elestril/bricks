PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

%.stl: configs.json
	openscad --backend Manifold -p configs.json -P $* -o $@ $(PROJECT_DIR)scad/bricks.scad

%.json: %.jsonnet
	jsonnet "$<" > "$@"
