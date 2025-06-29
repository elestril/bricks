include <brick.scad>;

module wall( 
  size, 
  studs = true, 
  sockets = true, 
  inputStl = "", inputStlMin = [0,0,0], inputStlMax = [0,0,0], 
  mirrorZ = 0, 
  bottomFill = 0
){ 
  union() {
    maybe_apply_sockets(size, sockets, fit="snug") 
      union() { 
        if (inputStl != "") { 
          socket_mirror([size.x * U, size.y * U, mirrorZ]) 
            translate([size.x * U , size.y * U, inputStlMax.z - inputStlMin.z ] / 2 + TR + inputStlMin)
            rotate(rot) 
            import(inputStl, center = true, convexity = 50);
          translate([ -0.5 * U, -4.4, 0 ]) cube([ size.x, size.y -1 , 0.5 ] * U + [0, 8.8, 0]);
        } else {
          brick_tr() brick_cube(size);
        }
      } 
    if (studs) brick_studs(size);
  }
}