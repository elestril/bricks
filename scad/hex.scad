include <BOSL2/std.scad>;
include <params.scad>;
use <stud.scad>;


// See https://www.redblobgames.com/grids/hexagons/#coordinates-cube 
AXIAL  = [
  [       1.5,       0,       0 ], 
  [ sqrt(3)/2, sqrt(3),       0 ], 
  [         0,       0,       1 ] 
] * 12.7;

module r_pattern(d_min=0, d_max=SIZE.x, z=0, coords=AXIAL) {
  d_max = d_max >= 0 ? d_max : d_min;
  for (q = [-d_max:1:d_max]) {
    for (r = [-d_max:1:d_max]) {
      d = max(abs(r), abs(q), abs(-r - q));
      if (d >= d_min && d <= d_max) {
        translate(coords * [r, q, z]) children();
      }
    }
  }
}

module rs_pattern(size=SIZE, coords=AXIAL) {
  for (q = [0:size.y-1]) {
    for (r = [0:size.x-1]) {
      translate(coords * [ r, q - floor(r / 2), size.z]) children();
    }
  }
}

module r_sockets(d = 1, a = 0, sockets = SOCKETS, fit = "snug") {
  if (sockets) {
    difference() {
      children();
      r_pattern(0, d, coords = 0.5 * AXIAL) rotate([0,0,a]) socket(fit, symmetry = 3);
    }
  } else {
    children();
  }
}

// Grid debossed in the surface
module hex_grid() {
  if (GRID) {
    difference() {
      children();
      translate([ 0, 0, SIZE.z * U - 0.4 ]) difference() {
        linear_extrude(height = 0.5) circle(r = U + 0.1, $fn = 6);
        linear_extrude(height = 1.2, center = true, scale = (U - 0.8) / U)
            circle(r = U - 0.1, $fn = 6);
      }
    }
  } else {
    children();
  }
}

module hex_base(z = SIZE.z) {
  intersection(){ 
    // cut out the sockets
    r_sockets(1, fit = (z > 0.25 ? "snug" : "loose"))
      // Base
      union() {
        regular_prism(6, r=U, h=z * U, anchor=BOT, chamfer1=((z>0.25) ? 0.0: 0.6), chamfer2=((GRID) ? 0.6: 0.0));
        if (STUDS) {
          r_pattern(0, 1, z=2*z, coords = 0.5 * AXIAL) stud();
        }
      }
    // cut studs to bounding box
    linear_extrude(height = z * U + 4) circle(r = U, $fn = 6); 
  }
}

module hex_r() {
      xyz_cuts() r_pattern(size = [SIZE.x, SIZE.y, 0]) hex_base();
}

module hex_s() {
  intersection() {
    hex_r();
    rotate([0,0,30]) linear_extrude(height = SIZE.z * U + 4) circle(r = sqrt(3) * SIZE.x * U, $fn = 6);
  }
}

module hex_l()  { 
      xyz_cuts() rs_pattern(size = [SIZE.x, SIZE.y, 0]) hex_base();
}