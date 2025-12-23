"""PythonSCAD equivalents of ``scad/stud.scad`` constructs.

The implementations below follow the same control-point coordinates used by the
OpenSCAD originals, but they return PythonSCAD ``PyOpenSCAD`` objects so that
callers can compose them directly inside ``.py`` generators (see
https://pythonscad.org/tutorial/site/ for API usage details).
"""

from typing import Iterable, Sequence
from enum import Enum

from openscad import PyOpenSCAD, circle, cube, linear_extrude, polygon, rotate_extrude, union

Point2D = Sequence[float]


class FitType(Enum):
    SNUG = "snug"
    LOOSE = "loose"

def stud() -> PyOpenSCAD:
    """Create the canonical LEGO-style stud using ``rotate_extrude``."""
    return rotate_extrude(
      polygon(
        points=[
        [0.0, -0.8],  # skirt start
        [2.4, -0.8],
        [2.4, 1.0],
        [2.6, 1.2],
        [2.6, 1.6],
        [2.4, 1.8],
        [0.0, 1.8]], convexity=2), convexity=2)

def _socket_profile_poly(fit: str) -> PyOpenSCAD:
    inset = 2.5 if fit == FitType.SNUG else 2.6
    return polygon(points=[
        [0.0, -0.4],
        [4.0, -0.4],
        [4.0, 2.2],
        [3.6, 2.2],
        [3.6, 0.0],
        [3.0, 0.0],
        [inset, 0.4],
        [inset, 1.2],
        [3.1, 1.6],
        [3.1, 2.2],
        [0.0, 2.2],
    ])
                   

_SOCKET_SYMMETRY_ANGLES = { 
    2: (0.0,),
    3: (0.0, 60.0, 120.0),
    4: (0.0, 90.0)
}

def socket(fit: FitType = FitType.SNUG, symmetry: int = 4) -> PyOpenSCAD:
    """Create a socket that mates with :func:`stud`.
    """
    body = rotate_extrude(_socket_profile_poly(fit), convexity=4)
    arms = [
        cube([7.2, 0.4, 4.4], center=True).rotate([0.0, 0.0, angle])
        for angle in _SOCKET_SYMMETRY_ANGLES.get(symmetry, [0.0])
    ]
    return union([body, *arms])


def socket_blank():
    """Return the blank socket cap used when studs are disabled."""

    base = linear_extrude(circle(r=3.0), height=0.6, scale=0.8)
    cap = linear_extrude(circle(r=2.4), height=1.2).translate([0.0, 0.0, 0.6])
    return base | cap
