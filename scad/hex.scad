include <params.scad>;
use <stud.scad>;

/* 
Transformation matrix: 
Axial (flat variant) to x-y cartesian coordinates.

See https://www.redblobgames.com/grids/hexagons/#coordinates-cube
*/
axial_coords = [ 
  [       1.5,       0 ], 
  [ sqrt(3)/2, sqrt(3) ], 
  [         0,       0 ] 
];

module hex_pattern(d_min, d_max=-1, unit = U) {
  d_max = d_max >= 0 ? d_max : d_min;
  for (q = [-d_max:1:d_max]) {
    for (r = [-d_max:1:d_max]) {
      d = max(abs(r), abs(q), abs(-r - q));
      if (d >= d_min && d <= d_max) {
        translate(unit * axial_coords * [ r, q ]) children();
      }
    }
  }
}

module hex_rect_pattern(x, y, unit = U) {
  for (q = [0:1:x-1]) {
    for (r = [0:1:y-1]) {
      translate(unit * axial_coords * [ r, q - floor(r / 2)]) children();
    }
  }
}

module hex_sockets(d = 1, a = 0, sockets = true, fit = "snug") {
  if (sockets) {
    difference() {
      children();
      hex_pattern(0, d, unit = 0.5 * U) rotate([0,0,a]) socket(fit, symmetry = 3);
    }
  } else {
    children();
  }
}

// Grid debossed in the surface
module hex_grid(grid = true) {
  if (grid) {
    difference() {
      children();
      translate([ 0, 0, size.z * U - 0.4 ]) difference() {
        linear_extrude(height = 0.5) circle(r = U + 0.1, $fn = 6);
        linear_extrude(height = 1.2, center = true, scale = (U - 0.8) / U)
            circle(r = U - 0.1, $fn = 6);
      }
    }
  } else {
    children();
  }
}

module hex_base(z = 0.25, studs=false, sockets=false, socket_angle = 0, grid=false) {
  intersection(){ 
    // cut out the sockets
    hex_sockets(1, a = socket_angle, sockets = sockets, fit = (size.z > 0.25 ? "snug" : "loose"))
      // Base
      union() {
        // deboss grid
        hex_grid(grid)
          // the plain hex base 
          linear_extrude(height = z * U) circle(r = U, $fn = 6); // The actual base
        // Add studs
        if (studs) {
           hex_pattern(0, 1, unit = 0.5 * U) translate([ 0, 0, size.z ] * U) stud();
        }
      }
    // cut studs to bounding box
    linear_extrude(height = z * U + 4) circle(r = U, $fn = 6); 
  }
}

module hex_r(size, studs, sockets, grid = true) {
      hex_pattern(0, size.x) 
        hex_base(z=size.z, studs=studs, sockets=sockets, socket_angle=0, grid=grid);
}

module hex_s(size, studs, sockets, grid = true) {
  intersection() {
    hex_pattern(0, size.x) 
      hex_base(z=size.z, studs=studs, sockets=sockets, socket_angle=30, grid=grid);
    rotate([0,0,30]) linear_extrude(height = size.z * U + 4) circle(r = sqrt(3) * size.x * U, $fn = 6);
  }
}

module hex_linear(size, studs, sockets, grid = true)  { 
      hex_rect_pattern(size.x, size.y, U) 
        hex_base(z=size.z, studs=studs, sockets=sockets, socket_angle=0, grid=grid);
}