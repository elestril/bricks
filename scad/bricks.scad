include <params.scad>;
include <brick.scad>;
include <hex.scad>;

// Parameters

// label of brick to generate
type = "Brick";
subtype = "Wall";
label = "None";
studs = true;
sockets = true;
grid = true;

// Nominal size of the brick in units
size = [ 2, 1, 4 ]; // 0.25
rot = [0,0,0]; // [0, 90, 180, 270]

// Name of this brick
name = "";

// STL file to remix
inputStl = "";

// Offset of the input stl to normalize with the brick grid
inputStlMin = [0,0,0];

// Offset of the input stl to normalize with the brick grid
inputStlMax = size * U;

// Mirror z millimeters of the foot to patch any slots
mirrorZ = 7.0; // [0:0.1:100]

// Texture for tiles
floorTx = "";

module __Customizer_Limit__ () {}  // Hide following assignments from Customizer.

if (type == "Brick" ) { 
  brick(size, subtype, label, studs, sockets, inputStl, inputStlMin, inputStlMax, mirrorZ, floorTx);
} else if (type == "Hex-R") { 
  hex_r(size, subtype, label, studs, sockets);
} else if (type == "Hex-S") { 
  hex_s(size, subtype, label, studs, sockets);
}