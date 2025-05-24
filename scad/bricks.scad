include <params.scad>;
use <brick.scad>;
use <hex.scad>;

// Parameters

// Kind of brick to generate
class = "Brick";
type = "Wall";
kind = "None";
studs = true;
sockets = true;
grid = true;

// Nominal size of the brick in units
size = [ 2, 1, 4 ]; // 0.25

// Name of this brick
name = "";

// STL file to remix
inputStl = "";

// Offset of the input stl to normalize with the brick grid
inputStlOffset = [0,0,0]; // [-200, 0.1, 200]

// Mirror z millimeters of the foot to patch any slots
mirrorZ = 7.0; // [0:0.1:100]

// Texture for tiles
floorTx = "";

module __Customizer_Limit__ () {}  // Hide following assignments from Customizer.

if (class == "Brick") { 
  brick(size, type, kind, studs, sockets, inputStl, inputStlOffset, mirrorZ, floorTx);
} else if (class == "Hex-R") { 
  hex_r(size, type, kind, studs, sockets);
} else if (class == "Hex-S") { 
  hex_s(size, type, kind, studs, sockets);
}