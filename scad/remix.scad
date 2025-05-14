include <params.scad>;
include <test.nfo>;
use <brick.scad>;

$fn = 180;
echo(filename);

input = "test.stl";
minv = [ -2.0, -0.5, 0.0 ];
maxv = [ 2.0, 0.5, 5.0 ];
offset = [ 0, 0, 0 ];
mirror = 7.2;

dim = maxv - minv;
// dim = [ 4, 1, 4 ];

union() {
  wall_reshape(dim, mirror) translate(([ -0.5, -0.5, 0 ] - minv) * U + offset)
      import(input, convexity = 12);

  brick_studs(dim);
}

/// #_tr() cube([ 4, 1, 0.25 ] * U);

// import(filename, convexity = 10);