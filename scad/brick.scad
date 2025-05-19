include <params.scad>;
use <stud.scad>;
use <texture.scad>;

// Brick, with the first grid position centered on 0,0

module _tr() { translate([ -0.5, -0.5, 0 ] * U) children(); }

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

module wall_bbox(size) {
  intersection() {
    union() {
      _tr() cube([ size.x, size.y, 0.5 ] * U);
      translate([ -0.5, -6, 0.5 ] * U) cube([ size.x, 12, size.z - 0.5 ] * U);
    }
    children();
  }
}

module wall_fill(size) {
  union() {
    translate([ -0.5, -0.25, 0 ] * U) cube([ size.x, size.y - 0.5, 0.5 ] * U);
    translate([ -0.5, -0.25, 0 ] * U) cube([ 0.5, 0.5, size.z ] * U);
    translate([ size.x - 1, -0.25, 0 ] * U) cube([ 0.5, 0.5, size.z ] * U);
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

module wall_reshape(size, mirror = 0) {
  union() {
    if (mirror) {
      wall_mirror([ size.x * U, size.y * U, mirror ]) wall_bbox(size)
          children();
    } else {
      wall_bbox(size) children();
    }
    wall_fill(size);
  }
}

module brick(size, studs = true, sockets = true, floor_tx = "") {
  intersection() {
    maybe_apply_sockets(size, sockets) union() {
      if (floor_tx) {
        _tr() cube(size * U - [ 0, 0, 0.9 ]);
        translate([ -0.5 * U, -0.5 * U, size.z * U - 0.9 ]) texture(floor_tx);
      } else {
        _tr() cube(size * U);
      }
      if (studs) {
        brick_studs(size);
      }
    }
    // translate([ -0.5 * U, -0.5 * U, -5 ]) cube(size * U + [ 0, 0, 10 ]);
  }
}