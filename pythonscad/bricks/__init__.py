"""PythonSCAD helpers that mirror the legacy OpenSCAD brick macros.

This package intentionally mirrors the structure of ``scad/stud.scad`` so that
new PythonSCAD entrypoints can reuse identical building blocks when migrating
away from the OpenSCAD templating workflow documented in README.md.
"""

from .stud import socket, socket_blank, stud

__all__ = ["stud", "socket", "socket_blank"]
