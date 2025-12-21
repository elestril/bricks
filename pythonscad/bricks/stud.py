"""PythonSCAD equivalents of ``scad/stud.scad`` constructs.

The implementations below follow the same control-point coordinates used by the
OpenSCAD originals, but they return PythonSCAD ``PyOpenSCAD`` objects so that
callers can compose them directly inside ``.py`` generators (see
https://pythonscad.org/tutorial/site/ for API usage details).
"""

from typing import Iterable, Sequence

from openscad import circle, cube, linear_extrude, polygon, rotate_extrude, union

Point2D = Sequence[float]


_STUD_PROFILE: list[list[float]] = [
    [0.0, -0.8],  # skirt start
    [2.4, -0.8],
    [2.4, 1.0],
    [2.6, 1.2],
    [2.6, 1.6],
    [2.4, 1.8],
    [0.0, 1.8],
]


def _stud_profile_poly():
    """Return the 2D polygon used for both studs and sockets."""

    return polygon(points=_STUD_PROFILE)


def stud(convexity: int = 2):
    """Create the canonical LEGO-style stud using ``rotate_extrude``."""

    return rotate_extrude(_stud_profile_poly(), convexity=convexity)


def _socket_profile_points(fit: str) -> list[list[float]]:
    snug = fit.lower() == "snug"
    inset = 2.5 if snug else 2.6
    return [
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
    ]


def _socket_profile_poly(fit: str):
    return polygon(points=_socket_profile_points(fit))


def _symmetry_angles(symmetry: int) -> Iterable[float]:
    if symmetry == 2:
        return (0.0,)
    if symmetry == 3:
        return (0.0, 60.0, 120.0)
    return (0.0, 90.0)


def socket(*, fit: str = "snug", symmetry: int = 4):
    """Create a socket that mates with :func:`stud`.

    The API mirrors ``socket(fit="snug", symmetry=4)`` from the SCAD source, but
    returns a PythonSCAD object that callers can union or difference just like
    any other primitive (see the "Combining objects" tutorial section).
    """

    body = rotate_extrude(_socket_profile_poly(fit), convexity=4)
    arms = [
        cube([7.2, 0.4, 4.4], center=True).rotate([0.0, 0.0, angle])
        for angle in _symmetry_angles(symmetry)
    ]
    return union([body, *arms])


def socket_blank():
    """Return the blank socket cap used when studs are disabled."""

    base = linear_extrude(circle(r=3.0), height=0.6, scale=0.8)
    cap = linear_extrude(circle(r=2.4), height=1.2).translate([0.0, 0.0, 0.6])
    return base | cap
