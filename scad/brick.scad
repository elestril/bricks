include <BOSL2/std.scad>;
include <params.scad>;
include <stud.scad>;
include <texture.scad>;

/**** Scale vectors ****/ 
SQUARE = [ 
  [1,0,0],
  [0,1,0],
  [0,0,1],
] * U;

// streched in x-direction, offset 0.5U from origin
LONG = [ 
  [sqrt(3),0,0],
  [      0,1,0],
  [      0,0,1],
] * U;

module xy_pattern(size, coords) { 
  for (sx = [0:size.x-1]) {
    for (sy = [0:size.y-1]) {
      translate(coords * [sx + 0.5,sy + 0.5, size.z]) children(); 
    }
  }
}

module xyz_cuts() { 
  difference() {
    children();
    if (CUT_X > -20 ) { 
      translate([CUT_X - 20, -10, 0] * U) cube(20 * U);
    }
    if (CUT_Y > -20 ) { 
      translate([-10, CUT_Y - 20, 0] * U) cube(20 * U);
    }
    if (CUT_Z > -20 ) { 
      translate([0,0, CUT_Z - 20] * U) cube(20 * U);
    }
  }
}

module xy_studs(size, coords, studs = STUDS) { 
  if (studs) {
    union() {
      children();
      xy_pattern(size, coords) stud(); 
    } 
  } else {
    children();
  } 
}

module xy_sockets(size, coords, fit = "snug", sockets = SOCKETS) {
  if (sockets) difference() {
    children();
    xy_pattern([size.x, size.y, 0], coords) socket(fit);
  }
  else
    children();
}

module brick_cube(size, coords) { 
  if (size.z < 0.26 && SOCKETS) { 
    cuboid(coords * size, p1 = [0,0,0], chamfer=0.6, edges=[BOT]);
  } else { 
    cuboid(coords * size, p1 = [0,0,0]);
  }
}

module socket_mirror(dim) {
  // Mirrors the front side of the tile to the back to cover the openlock slots.
  if (dim.z == 0) { 
    children();
  } else { 
    union() {
      mirror([ 0, 1, 0 ]) intersection() {
        translate([ -0.5, 0, 0 ] * U) cube(dim);
        children();
      }
      difference() {
        children();
        translate([ -0.5, 0, 0 ] * U - [ 0, dim.y, 0 ]) cube(dim);
      }
    }
  }
}

module brick(coords=SQUARE, size = SIZE){
    xyz_cuts() xy_sockets(size, coords) xy_studs(size, coords) {
        // Check if this is a textured tile
        if (TEXTURE != "undef" && TEXTURE != "") {
            // Create base cube slightly shorter to accommodate texture
            translate([0, 0, 0])
                cuboid(coords * [size.x, size.y, size.z - 0.9/U], p1 = [0,0,0]);
            // Add texture surface on top
            translate([-0.5, -0.5, size.z - 0.9/U] * U)
                texture(TEXTURE);
        } else {
            // Standard brick without texture
            brick_cube(size, coords);
        }
    }
}
/*
module brick() {
  union() {
    brick_sockets(size, sockets, fit = size.z > 0.25 ? "snug" :"loose") 
      union() { 
        // ***  This is a remix  ***
        if (input != "") { 
          if (mirrorZ > 0) { 
            socket_mirror([size.x * U, size.y * U, mirrorZ]) 
              translate([size.x * U , size.y * U, inputMax.z - inputMin.z ] / 2 + TR + inputMin)
              rotate(rot) 
              import(inputStl, center = true, convexity = 50);
            translate([ -0.5 * U, -4.4, 0 ]) cube([ size.x, size.y -1 , 0.5 ] * U + [0, 8.8, 0]);
         } else {
            translate(TR - inputMin)
            import(input, convexity = 50);
            translate(TR) cube([size.x * U , size.y * U , bottomFill]);
          }
        }
        // *** This is a textured floor tile ***
        else if (texture) {
          cube(size * U - [ 0, 0, 0.9 ]);
          translate([ -0.5 * U, -0.5 * U, size.z * U - 0.9 ]) texture(floorTx);
        // ***  This is a blank
        } else {
          brick_cube(size);
        }
      } 
    if (studs) brick_studs(size);
  }
}
*/