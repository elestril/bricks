include <params.scad>;
use <brick.scad>;
use <hex.scad>;
use <stud.scad>;

size = [ 4, 1, 4 ];
// brick(size);
// hex_r(2, sockets = false);
color("orange") hex_s(2, z = 0.25, sockets = true);
// hex_grid(4);