%.brick.stl: %.json
	openscad -o $@ $<

%.json: %.stl bin/stlinfo.py
	./bin/stlinfo.py "$<" "$@"
