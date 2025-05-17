include ../Makefile.mk

CONFIGS := $(shell jq -r '.["parameterSets"].[].name' < configs.json)

bricks: configs.json stl

stl: $(CONFIGS:=.stl)

.PHONY: clean
clean: 
	rm -f *.stl *.json