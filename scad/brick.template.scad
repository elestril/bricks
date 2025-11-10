// Geometric class of the brick
FAMILY = "{family}"; // [Square,Long,SquareHex,Hex,HexR,HexS]

// Enable studs
STUDS = {studs};

// Enable sockets
SOCKETS = {sockets};

// Deboss grid
GRID = {grid};

// Nominal size of the brick in units
SIZE = {size}; // 0.25

// Rotation of the brick
ROT = {rot}; // [0, 90, 180, 270]

// STL file to remix
INPUT = "{input}";

// Offset of the input stl to normalize with the brick grid
INPUTMIN = {inputMin};

// Offset of the input stl to normalize with the brick grid
INPUTMAX = {inputMax};

// Mirror z millimeters of the foot to patch any slots
MIRRORZ = {mirrorZ}; // [0:0.1:10]

// Fill that much of the bottom
BOTTOMFILL = {bottomFill}; // [0:0.1:10]


// Cut along X axis
CUT_X = {cutX}; // [-99.0:0.25:20.0]

// Cut along Y axis
CUT_Y = {cutY}; // [-99.0:0.25:20.0]

// Cut along Z axis
CUT_Z = {cutZ}; // [-99.0:0.25:20.0]


// Texture for tiles
TEXTURE = "{texture}";

module __Customizer_Limit__ () {{}} // Hide following assignments from Customizer.

include <params.scad>;
include <brick.scad>;
include <hex.scad>;

if (FAMILY == "Square") {{
  brick(SQUARE);
}} else if (FAMILY == "Long") {{
  brick(LONG);
}} else if (FAMILY == "Hex") {{
  hex_l();
}} else if (FAMILY == "HexR") {{ 
  hex_r();
}} else if (FAMILY == "HexS") {{ 
  hex_s();
}}