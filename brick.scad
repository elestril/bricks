include <params.scad>;
module brick(x = 1, y = 1, z = 0.25, studs = true, ) {
  union() {
    translate([ -0.5 * u, -0.5 * u, 0 ]) cube([ x * u, y * u, z * u ]);
    if (studs) {
      for (sx = [0:x - 1])
        for (sy = [0:y - 1]) translate([ sx * u, sy * u, z * u ]) stud();
    }
  }
}