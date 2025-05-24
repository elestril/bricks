include <params.scad>;
use <stud.scad>;

cube_coords = [ 
  [ 1.5, 0 ], 
  [ sqrt(3) / 2, sqrt(3) ], 
  [ 0, 0 ] 
];

module hex_pattern(mind, maxd = -1, unit = U) {
  maxd = maxd >= 0 ? maxd : mind;
  for (q = [-maxd:1:maxd]) {
    for (r = [-maxd:1:maxd]) {
      d = max(abs(r), abs(q), abs(-r - q));
      if (d >= mind && d <= maxd) {
        translate(unit * cube_coords * [ r, q ]) children();
      }
    }
  }
}

module hex_sockets(d = 1, sockets = true, edge_blank = false, fit = "snug") {
  if (sockets) {
    difference() {
      children();
      hex_pattern(0, edge_blank ? d -1 : d, unit = 0.5 * U) socket(fit);
      if (edge_blank) hex_pattern(d, unit = 0.5 * U) socket_blank();
    }
  } else {
    children();
  }
}

// Grid debossed in the surface
module hex_grid(size, grid = true) {
  if (grid) {
    difference() {
      children();
      translate([ 0, 0, size.z * U - 0.4 ]) hex_pattern(0, size.x, U) difference() {
        linear_extrude(height = 0.5) circle(r = U + 0.1, $fn = 6);
        linear_extrude(height = 1.2, center = true, scale = (U - 0.8) / U)
            circle(r = U - 0.1, $fn = 6);
      }
    }
  } else {
    children();
  }
}

module hex_base(z = 0.25, stud = true, socket = true) {
  linear_extrude(height = z * U) circle(r = U, $fn = 6);
}

module hex_r(size, type, kind, studs, sockets, grid = true) {
  intersection() {
    hex_sockets(size.x, sockets, 
    edge_blank = (size.x > 1), 
    fit = (size.z > 0.25 ? "snug" : "loose")
    )
    union() {
      hex_grid(size, grid) hex_pattern(0, size.x, U)
          hex_base(size.z, stud = false, socket = false);
      hex_pattern(0, 2 * size.x + 1, unit = 0.5 * U) translate([ 0, 0, size.z ] * U)
          stud();
    }
    hex_pattern(0, size.x, U) hex_base(size.z + 0.5);
  }
}

module hex_s(size, type, kind, studs, sockets, grid = true) {
  intersection() {
    hex_sockets(size.x * 2 + 1, sockets, edge_blank = false, fit = size.z > 0.25 ? "snug" : "loose") union() {
      hex_grid(size, grid) rotate([0,0,30]) linear_extrude(height = size.z * U) circle(r = sqrt(3) * size.x  * U, $fn = 6);

      hex_pattern(0, 2 * size.x, unit = 0.5 * U) translate([ 0, 0, size.z ] * U)
          stud();
    }
    rotate([0,0,30]) linear_extrude(height = (size.z + 0.5) * U) circle(r = sqrt(3) * size.x * U, $fn = 6);
  }
}