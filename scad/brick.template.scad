include <brick.scad>;

family = "{family}";
subfamily = "{subfamily}";
set = "{set}";
studs = {studs};
sockets = {sockets};
grid = {grid};

// Nominal size of the brick in units
size = {size}; // 0.25

// Rotation of the brick
rot = {rot}; // [0, 90, 180, 270]

// Name of this brick
name = "{name}";

// STL file to remix
input = "{input}";

// Offset of the input stl to normalize with the brick grid
inputMin = {inputMin};

// Offset of the input stl to normalize with the brick grid
inputMax = {inputMax};

// Mirror z millimeters of the foot to patch any slots
mirrorZ = {mirrorZ}; // [0:0.1:10]

// Fill that much of the bottom
bottomFill = {bottomFill}; // [0:0.1:10]

// Texture for tiles
texture = "{texture}";

module __Customizer_Limit__ () {{}} // Hide following assignments from Customizer.

if (family == "Square" ) {{ 
  brick(size, subfamily, studs, sockets, input, inputMin, inputMax, mirrorZ, bottomFill, texture);
}} else if (family == "Hex-R") {{ 
  hex_r(size, subfamily, studs, sockets);
}} else if (family == "Hex-S") {{ 
  hex_s(size, subfamily, studs, sockets);
}}