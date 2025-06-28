include <params.scad>;
include <brick.scad>;
include <hex.scad>;

// Parameters

// label of brick to generate
family = "Square";
genus = "Wall";
studs = true;
sockets = true;
grid = true;

// Nominal size of the brick in units
size = [ 2, 1, 4 ]; // 0.25
rot = [0,0,0]; // [0, 90, 180, 270]

// Name of this brick
name = "";

// STL file to remix
input = "";

// Offset of the input stl to normalize with the brick grid
inputStlMin = [0,0,0];

// Offset of the input stl to normalize with the brick grid
inputStlMax = size * U;

// Mirror z millimeters of the foot to patch any slots
mirrorZ = 7.0; // [0:0.1:10]

// Fill that much of the bottom
bottomFill = 7.2; // [0:0.1:10]

// Texture for tiles
floorTx = "";

module __Customizer_Limit__ () {}  // Hide following assignments from Customizer.

if (family == "Square" ) { 
  brick(size, genus, studs, sockets, input, inputStlMin, inputStlMax, mirrorZ, bottomFill, floorTx);
} else if (family == "Hex-R") { 
  hex_r(size, genus, studs, sockets);
} else if (family == "Hex-S") { 
  hex_s(size, genus, studs, sockets);
}