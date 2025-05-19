HIRES = $(wildcard hires/*.png)
TEXTURES = $(notdir $(HIRES))

all: $(TEXTURES)

%.png: hires/%.png
	convert $< -resize 255x255  -type Grayscale -level 16 -auto-level -depth 8 $@

.PHONY: clean
clean:
	rm -f *.png

