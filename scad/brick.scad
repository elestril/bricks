include <params.scad>;
use <stud.scad>;

// Brick, with the first grid position centered on 0,0

module _tr() { translate([ -0.5, -0.5, 0 ] * U) children(); }

module brick_studs(units) {
  for (sx = [0:units.x - 1])
    for (sy = [0:units.y - 1]) translate([ sx, sy, units.z ] * U) stud();
}

module brick_sockets(units) {
  for (sx = [0:units.x - 1])
    for (sy = [0:units.y - 1]) translate([ sx, sy, 0 ] * U) socket();
}

module maybe_apply_sockets(units, sockets = true) {
  if (sockets) difference() {
      children();
      brick_sockets(units);
    }
  else
    children();
}

module wall_bbox(units) {
  intersection() {
    union() {
      _tr() cube([ units.x, units.y, 0.5 ] * U);
      translate([ -0.5, -6, 0.5 ] * U) cube([ units.x, 12, units.z - 0.5 ] * U);
    }
    children();
  }
}

module wall_fill(units) {
  union() {
    translate([ -0.5, -0.25, 0 ] * U) cube([ units.x, units.y - 0.5, 0.5 ] * U);
    translate([ -0.5, -0.25, 0 ] * U) cube([ 0.5, 0.5, units.z ] * U);
    translate([ units.x - 1, -0.25, 0 ] * U) cube([ 0.5, 0.5, units.z ] * U);
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

module wall_reshape(units, mirror = 0) {
  union() {
    if (mirror) {
      wall_mirror([ units.x * U, units.y * U, mirror ]) wall_bbox(units)
          children();
    } else {
      wall_bbox(units) children();
    }
    wall_fill(units);
  }
}

module brick(units, studs = true, sockets = true) {
  maybe_apply_sockets(units, sockets) union() {
    _tr() cube(units * U);
    if (studs) {
      brick_studs(units);
    }
  }
}