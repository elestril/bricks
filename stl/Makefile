
TOPTARGETS := all clean stl
SUBDIRS := $(wildcard */.)

CONFIGS := $(SUBDIRS:=/configs.json)


BRICKS := $(shell jq -r '.["parameterSets"].[].name' < configs.json)

bricks: config stl

stl: $(BRICKS:=.stl)

%.stl: configs.json
	openscad --backend Manifold -p configs.json -P $* -o $@ ../scad/bricks.scad

config: $(CONFIGS)
$(CONFIGS): configs.jsonnet
	jsonnet -o $@ $<

.PHONY: clean
clean: 
	rm -f *.stl *.json

$(TOPTARGETS): $(SUBDIRS)
$(SUBDIRS): 
	$(MAKE) -C $@ $(MAKECMDGOALS)

.PHONY: $(TOPTARGETS) $(SUBDIRS)