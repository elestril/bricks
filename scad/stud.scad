/***  Stud/Socket Geometry  ***

socket      stud
__          ______________________
  \        /E                     |
   \      D                       Y
    |     |
     C    C                       A
      \    \                      x
       B    B                     i
       |    |                     s
       |    |
       A    |                     |
     /      |                     |
----/       |--- X Axis ----------+
            |                     |
            A_____________________|

********************************/

module stud() { rotate_extrude(convexity = 2) stud_poly(); }

module stud_poly() {
  polygon([
    [ 0.0, -0.4 ],  //
    [ 2.4, -0.4 ],  // A
    [ 2.4, 1.0 ],   // B
    [ 2.6, 1.2 ],   // C
    [ 2.6, 1.6 ],   // D
    [ 2.4, 1.8 ],   // E
    [ 0.0, 1.8 ]
  ]);
}

module socket(fit="snug") {
  union() {
    rotate_extrude(convexity = 4) socket_poly(fit);
    for (a = [ 0, 90 ])
      rotate([ 0, 0, a ]) cube([ 7.2, 0.4, 4.4 ], center = true);
  }
}

module socket_blank() {
  linear_extrude(0.6, scale = 0.8) { circle(r = 3.0); }
  translate([ 0, 0, 0.6 ]) linear_extrude(1.2) { circle(r = 2.4); }
}

module socket_poly(fit="snug") {
  polygon([
    [ 0.0, -0.4 ],  //
    [ 4.0, -0.4 ],  //
    [ 4.0, 2.2 ],   //
    [ 3.6, 2.2 ], 
    [ 3.6, 0.0 ],
    [ 3.0, 0.0 ],   //
    fit == "snug" ? [ 2.5, 0.4 ] : [2.6, 0.4],   // A
    fit == "snug" ? [ 2.5, 1.2 ] : [2.6, 1.2],   // B
    [ 3.1, 1.6 ],   //
    [ 3.1, 2.2 ], 
    [ 0.0, 2.2 ]    //
  ]);
}