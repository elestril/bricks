%.brick.stl: %.brick.json
	openscad --backend Manifold -p $< -P default -o $@  remix.scad

%.brick.json: %.stl ../bin/stlinfo.py
	../bin/stlinfo.py --stl $< --json_output $@