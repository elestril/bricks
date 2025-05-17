include Makefile.mk

TOPTARGETS := all clean
SUBDIRS := $(wildcard */.)

all: $(SUBDIRS) stl

stl:
	$(MAKE) -C stl stl

$(TOPTARGETS): $(SUBDIRS)
$(SUBDIRS): 
	$(MAKE) -C $@ $(MAKECMDGOALS)

.PHONY: $(TOPTARGETS) $(SUBDIRS) stl