"""
Global constants and utilities for the brick configuration system.

This module defines shared constants like the base directory and grid unit size,
as well as utility functions for accessing configuration paths.
"""

import pathlib

from absl import flags

# Base directory of the project (2 levels up from this file)
BASEDIR = pathlib.Path(__file__).resolve().parents[2].relative_to(pathlib.Path('.').resolve(), walk_up=True)

# Grid unit size: one unit = 0.5 inches = 12.7mm
U = 12.7

# Command-line flag for OpenSCAD files path
flags.DEFINE_string('scadpath', str(BASEDIR.joinpath('scad')), 'Path to the scad files')
FLAGS = flags.FLAGS

# Cached OpenSCAD path
_SCADPATH = None

def scadpath() -> pathlib.Path:
  """Get the resolved path to the OpenSCAD files directory.

  This function caches the resolved path on first call for better performance.

  Returns:
    pathlib.Path: Absolute path to the OpenSCAD files directory
  """
  global _SCADPATH
  if not _SCADPATH:
    _SCADPATH = pathlib.Path(FLAGS.scadpath).resolve()
  return _SCADPATH