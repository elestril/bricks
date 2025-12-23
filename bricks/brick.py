"""PythonSCAD helpers that mirror ``scad/brick.scad`` primitives."""

from __future__ import annotations

import math
import numpy
from typing import Any, Mapping, Protocol, Sequence


from bricks import stud, Point
from openscad import PyOpenSCAD, cube, union, print

UNIT = 12.7

SQUARE_COORDINATES = numpy.matrix([ 
  [1,0,0],
  [0,1,0],
  [0,0,1],
]) * UNIT

LONG_COORDINATES = numpy.matrix([
  [math.sqrt(3),0,0],
  [      0,1,0],
  [      0,0,1],
]) * UNIT

class Brick(): 
    def __init__(self, size: Point):
      self.size = size

    def render(self) -> PyOpenSCAD:
      return(cube(self.size))
    



def _xy_pattern(size: Point, coords: numpy.matrix, feature: PyOpenSCAD) -> PyOpenSCAD:
    """Return a pattern tiled across the X-Y face defined by ``size``."""
    objs = []
    for ix in range(size.x):
        for iy in range(size.y):
            objs.append(feature.translate( coords * [ix + 0.5, iy + 0.5, size.z]))
    return union(objs)
