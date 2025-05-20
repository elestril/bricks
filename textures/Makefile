
# convert $$< -resize \(.size) -type Grayscale -level 16 -auto-level -gamma \(.gamma) -depth 8 -evaluate divide 25.5 -evaluate multiply 25.5 $$@
define CONVERT
	convert $$< -resize \(.size) -type Grayscale -level 16  -gamma \(.gamma) -auto-level -depth 8 -evaluate divide 51 $$@
endef


TEXTURES := $(shell jq -r 'keys[]' < textures.json)
$(foreach tex,$(TEXTURES),$(call $(eval $(shell jq -r '.$(tex) | "$(tex).png: \(.input);\t$(CONVERT)"' < textures.json))))

.PHONY: debug
debug: textures.json 

all: $(TEXTURES:=.png)

.PHONY: clean
clean:
	rm -f *.png

