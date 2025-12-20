// Geometric class of the brick
FAMILY = "Square"; // [Square,Long,SquareHex,Hex,HexR,HexS]

// Enable studs
STUDS = false;

// Enable sockets
SOCKETS = true;

// Deboss grid
GRID = true;

// Nominal size of the brick in units
SIZE = [2, 2, 0.25]; // 0.25

// Rotation of the brick
ROT = [0, 0, 0]; // [0, 90, 180, 270]

// STL file to remix
INPUT = "";

// Offset of the input stl to normalize with the brick grid
INPUTMIN = [0, 0, 0];

// Offset of the input stl to normalize with the brick grid
INPUTMAX = [0, 0, 0];

// Mirror z millimeters of the foot to patch any slots
MIRRORZ = 0.0; // [0:0.1:10]

// Fill that much of the bottom
BOTTOMFILL = 0.0; // [0:0.1:10]


// Cut along X axis
CUT_X = -99; // [-99.0:0.25:20.0]

// Cut along Y axis
CUT_Y = -99; // [-99.0:0.25:20.0]

// Cut along Z axis
CUT_Z = -99; // [-99.0:0.25:20.0]


// Texture for tiles
TEXTURE = "../textures/wood_planks.png";

module __Customizer_Limit__ () {} // Hide following assignments from Customizer.

include <params.scad>;
include <brick.scad>;
include <hex.scad>;

if (FAMILY == "Square") {
  brick(SQUARE);
} else if (FAMILY == "Long") {
  brick(LONG);
} else if (FAMILY == "Hex") {
  hex_l();
} else if (FAMILY == "HexR") { 
  hex_r();
} else if (FAMILY == "HexS") { 
  hex_s();
}
