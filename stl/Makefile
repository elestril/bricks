
SUBDIRS = $(patsubst %/.,%,$(wildcard */.))
JSON_CONFIGS = $(SUBDIRS:=/configs.json)

configs: $(JSON_CONFIGS)
$(JSON_CONFIGS): configs.jsonnet
	jsonnet -o $@ $<

define BRICKS_dir =
$(1)_STL = $$(addprefix $(1)/, $(shell jq -r '.["parameterSets"].[].stl' < $(1)/configs.json)) 
STL_FILES += $$($(1)_STL)

$(1)/%.stl: $(1)/configs.json configs;
	@mkdir -p $(1)/$$(dir $$(*))
	openscad --backend Manifold -p $(1)/configs.json -P $$(basename $$(notdir $$(*))) -o $$@ ../scad/bricks.scad

endef

$(foreach subdir, $(SUBDIRS), $(eval $(call BRICKS_dir,$(subdir))))

stl: $(STL_FILES)

.PHONY: clean
clean: 
	rm -f $(wildcard **/*.stl **/*.json)

.PHONY: $(TOPTARGETS) $(SUBDIRS)