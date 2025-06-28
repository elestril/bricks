include <BOSL2/std.scad>;
include <params.scad>;
include <stud.scad>;
include <texture.scad>;

// Brick, with the first grid position centered on 0,0
TR = [-0.5,-0.5,0] * U;

module brick_tr() { translate(TR) children(); }

module brick_studs(size) {
  for (sx = [0:size.x - 1])
    for (sy = [0:size.y - 1]) translate([ sx, sy, size.z ] * U) stud();
}

module brick_sockets(size, fit) {
  for (sx = [0:size.x - 1])
    for (sy = [0:size.y - 1]) translate([ sx, sy, 0 ] * U) socket(fit);
}

module maybe_apply_sockets(size, sockets = true, fit) {
  if (sockets) difference() {
      children();
      brick_sockets(size, fit);
    }
  else
    children();
}

module brick_cut(size, genus = "Generic") { 
  intersection() { 
  if (genus == "Wall") {
    union() {
    // Allow singnificant overhangs in the Y direction for walls.
      translate(TR)  cube([ size.x, size.y, 0.5 ] * U);
      translate([ -0.5, -6, 0.5 ] * U) cube([ size.x, 12, size.z - 0.5 ] * U);
    }
  } else { 
    // Cut to nominal size
     translate(TR) cuboid(size * U, anchor = FRONT+LEFT+BOTTOM, chamfer=0.8, edges=BOTTOM);
  }
  children();
  }
}

module brick_cube(size) { 
  cube(size * U);
}

module socket_mirror(size) {
  // Mirrors the front side of the tile to the back to cover the openlock slots.
  if (size.z == 0) { 
    children();
  } else { 
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
}

module brick(size, genus, studs = true, sockets = true, inputStl = "", inputStlMin = [0,0,0], inputStlMax = [0,0,0], mirrorZ = 0, bottomFill = 0, floorTx = "") {
  union() {
    maybe_apply_sockets(size, sockets, fit = size.z > 0.25 ? "snug" :"loose") brick_cut(size, genus)  
      union() { 
        // ***  This is a remix  ***
        if (inputStl != "") { 
          if (genus == "Wall") { 
            socket_mirror([size.x * U, size.y * U, mirrorZ]) 
              translate([size.x * U , size.y * U, inputStlMax.z - inputStlMin.z ] / 2 + TR + inputStlMin)
              rotate(rot) 
              import(inputStl, center = true, convexity = 50);
            translate([ -0.5 * U, -4.4, 0 ]) cube([ size.x, size.y -1 , 0.5 ] * U + [0, 8.8, 0]);
          } else if (size.z < 0.5 ) { 
              translate(size * U / 2 + TR + inputStlMin + (inputStlMax -size * U) * [0,0,0.5]) 
              rotate(rot) 
              import(inputStl, center = true, convexity = 50);
            translate(TR) cube([size.x * U, size.y * U, 2.6]);
          } else {
            translate(TR - inputStlMin)
            import(inputStl, convexity = 50);
            translate(TR) cube([size.x * U , size.y * U , bottomFill]);
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
      } 
    if (studs) brick_studs(size);
  }
}