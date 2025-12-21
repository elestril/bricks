#!/usr/bin/env pythonscad
"""Recreate Blank-Wall-4x1 using PythonSCAD primitives.

Running ``pythonscad reference.py`` exports Reference/Walls/Blank-Wall-4x1.stl
with geometry equivalent to the OpenSCAD workflow (SIZE=[4,1,4], studs+sockets).

Use ``--output <path>`` to override the destination when running in CI/tests.
"""

import argparse
import os
from pathlib import Path
from typing import Iterable, Sequence

from openscad import cube, export, show, union

from bricks import socket, stud

U = 12.7
SIZE = (4.0, 1.0, 4.0)
DEFAULT_OUTPUT = Path("Reference/Walls/Blank-Wall-4x1.stl")
ENV_OUTPUT_KEY = "PYTHONSCAD_OUTPUT"


def _grid_offsets(size: Sequence[float], z_units: float) -> Iterable[list[float]]:
    x_count, y_count = (int(round(size[0])), int(round(size[1])))
    for sx in range(x_count):
        for sy in range(y_count):
            yield [
                (sx + 0.5) * U,
                (sy + 0.5) * U,
                z_units * U,
            ]


def blank_wall(size: Sequence[float] = SIZE, studs_enabled: bool = True, sockets_enabled: bool = True):
    body = cube([size[0] * U, size[1] * U, size[2] * U])

    if sockets_enabled:
        sockets = [socket().translate(pos) for pos in _grid_offsets(size, 0.0)]
        if sockets:
            body = body.difference(union(sockets))

    if studs_enabled:
        studs = [stud().translate(pos) for pos in _grid_offsets(size, size[2])]
        if studs:
            body = body | union(studs)

    return body


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Blank-Wall-4x1 geometry")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Destination STL path (defaults to Reference/Walls/Blank-Wall-4x1.stl)",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    wall = blank_wall()
    env_override = os.environ.get(ENV_OUTPUT_KEY)
    output_path = Path(env_override) if env_override else args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    export(wall, str(output_path))
    show(wall)


if __name__ == "__main__":
    main()
