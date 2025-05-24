include <params.scad>;
use <stud.scad>;
use <texture.scad>;

// Brick, with the first grid position centered on 0,0o
TR = [-0.5,-0.5,0] * U;

module brick_tr() { translate(TR) children(); }

module brick_studs(size) {
  for (sx = [0:size.x - 1])
    for (sy = [0:size.y - 1]) translate([ sx, sy, size.z ] * U) stud();
}

module brick_sockets(size) {
  for (sx = [0:size.x - 1])
    for (sy = [0:size.y - 1]) translate([ sx, sy, 0 ] * U) socket();
}

module maybe_apply_sockets(size, sockets = true) {
  if (sockets) difference() {
      children();
      brick_sockets(size);
    }
  else
    children();
}

module wall_box(size) {
  intersection() {
    // Walls are trimmed to fit below z=0.5U, and have a very wide box in the Y-axis above that.
    union() {
      brick_tr() cube([ size.x, size.y, 0.5 ] * U);
      translate([ -0.5, -6, 0.5 ] * U) cube([ size.x, 12, size.z - 0.5 ] * U);
    }
    children();
  }
}

module brick_cube(size) { 
  cube(size * U);
}

module wall_fill(size) {
  union() {
    translate([ -0.5, -0.25, 0 ] * U) cube([ size.x, size.y - 0.5, 0.5 ] * U);
    // translate([ -0.5, -0.25, 0 ] * U) cube([ 0.5, 0.5, size.z ] * U);
    // translate([ size.x - 1, -0.25, 0 ] * U) cube([ 0.5, 0.5, size.z ] * U);
  }
}

module wall_mirror(size) {
  union() {
    mirror([ 0, 1, 0 ]) intersection() {
      translate([ -0.5, 0, 0 ] * U) cube(size);
      children();
    }
    difference() {
      children();
      translate([ -0.5, 0, 0 ] * U - [ 0, size.y, 0 ]) cube(size);
    }
  }
}


module brick_reshape(size) {
  union() {
    intersection() {
      translate(TR) brick_cube(size);
      children();
    }
    // Add solid base
    translate(TR) cube([ size.x * U, size.y * U, 2]);
  }
}

module wall_reshape(size, mirrorZ = 0) {
  union() {
    if (mirrorZ) {
      wall_mirror([ size.x * U, size.y * U, mirrorZ ]) wall_box(size)
          children();
    } else {
      wall_box(size) children();
    }
    wall_fill(size);
  }
}

module brick(size, kind, studs = true, sockets = true, inputStl = "", inputStlOffset = [0,0,0], mirrorZ = 0, floorTx = "") {
  intersection() {
    maybe_apply_sockets(size, sockets) union() { 
      // ***  This is a remix  ***
      if (inputStl != "") { 
        if (kind == "Wall") { 
          wall_reshape(size, mirrorZ) translate(TR + inputStlOffset) import(inputStl, convexity = 50);
        } else if (size.z < 0.5 ) { 
          translate(TR + inputStlOffset) import(inputStl, convexity = 50);
          translate(TR) cube([size.x * U, size.y * U, 2]);
        } else {
          translate(TR + inputStlOffset) import(inputStl, convexity = 50);
          translate(TR) cube([size.x, size.y, 5]);
        }
      }

      // *** This is a textured floor tile ***
      else if (floorTx) {
        brick_tr() cube(size * U - [ 0, 0, 0.9 ]);
        translate([ -0.5 * U, -0.5 * U, size.z * U - 0.9 ]) texture(floorTx);

      // ***  This is a blank
      } else {
        brick_tr() brick_cube(size);
      }

      if (studs) {
        brick_studs(size);
      }
    }
    translate(TR) brick_cube(size);
  }
}