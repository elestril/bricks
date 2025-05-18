include Makefile.mk

TOPTARGETS := all stl clean distclean

SUBDIRS = $(wildcard */.)
CONFIGS = $(SUBDIRS:/.=/configs.json)

all: configs stl

stl: configs $(SUBDIRS)

configs: $(CONFIGS)
$(CONFIGS): configs.jsonnet
	jsonnet -o $@ $<

$(SUBDIRS): 
	$(MAKE) -C $@ $(MAKECMDGOALS)

.PHONY: $(TOPTARGETS) $(SUBDIRS)