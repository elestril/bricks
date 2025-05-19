include <params.scad>;
use <brick.scad>;

// Parameters

// Kind of brick to generate
type = "Brick";
kind = "None";
studs = true;
sockets = true;

// Nominal size of the brick in units
size = [ 2, 1, 4 ];

// Name of this brick
name = "";

if (type == "Brick") {
  brick(size);
}

if (kind == "None") {
  echo("No configuration");
}