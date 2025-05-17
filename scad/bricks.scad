include <params.scad>;
use <brick.scad>;

// Parameters

// Kind of brick to generate
kind = "None";

// Nominal size of the brick in units
size = [ 2, 1, 4 ];

// Name of this brick
name = "";

echo("Name:", name, " Kind: ", kind, " Size: ", size);

if (kind == "Brick") {
  brick(size);
}

if (kind == "None") {
  echo("No configuration");
}

/*
input = "test.stl";
minv = [ -2.0, -0.5, 0.0 ];
maxv = [ 2.0, 0.5, 5.0 ];
offset = [ 0, 0, 0 ];
mirror = 7.2;


/*
        // dim = [ 4, 1, 4 ];

        union() {
          wall_reshape(dim, mirror) translate(([ -0.5, -0.5, 0 ] - minv) * U +
        offset) import(input, convexity = 12);

          brick_studs(dim);
        }

        /// #_tr() cube([ 4, 1, 0.25 ] * U);

        // import(filename, convexity = 10);

        */