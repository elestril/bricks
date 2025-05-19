include <params.scad>;
use <brick.scad>;
use <hex.scad>;
use <stud.scad>;

floor_tx = "../textures/stylized_wood_planks.png";
studs = false;

size = [ 4, 4, 0.25 ];
brick(size, studs = false, floor_tx = floor_tx);

// translate([ -0.5 * U, -0.5 * U, 0 ])
// surface(file = floor_tx);
// surface(file = "test_tx.dat", convexity = 10);