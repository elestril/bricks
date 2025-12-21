"""
Brick module defining the core Brick class and configuration.

This module provides the Brick class which represents a single 3D printable
brick with its dimensions, type, features (studs, sockets, grid), and
configuration parameters for OpenSCAD generation.
"""

from __future__ import annotations

import collections
import json
import pathlib

from absl import logging
from collections import UserDict
from functools import lru_cache
from typing import Any, Dict, Tuple

class InvalidBrick(ValueError):
  """Exception raised when a brick configuration is invalid."""
  pass

@lru_cache(maxsize=1)
def load_textures() -> Dict[str, Any]:
  """Load texture definitions from textures.json.

  Returns:
    Dictionary mapping texture names to their definitions
  """
  textures_path = pathlib.Path(__file__).parent.parent.parent / 'textures' / 'textures.json'
  try:
    with open(textures_path, 'r') as f:
      return json.load(f)
  except (FileNotFoundError, json.JSONDecodeError) as e:
    logging.warning(f'Could not load textures.json: {e}')
    return {}

def resolve_texture_path(texture_name: str) -> str:
  """Resolve a texture name to its file path.

  If the texture name is in textures.json, returns the path from the 'file' field.
  Otherwise, assumes it's already a file path and returns it as-is.

  Args:
    texture_name: Texture name or file path

  Returns:
    Path to the texture file (relative to scad directory: ../textures/filename.png)
  """
  textures = load_textures()

  # Check if this is a known texture name
  if texture_name in textures:
    texture_def = textures[texture_name]
    # Use 'file' field if present, otherwise use 'name.png'
    filename = texture_def.get('file', f"{texture_name}.png")
    return f"../textures/{filename}"

  # If not in textures.json, check if it's already a path
  if '/' in texture_name or texture_name.endswith('.png'):
    return texture_name

  # Otherwise treat as a texture name and construct path
  return f"../textures/{texture_name}.png"

class Brick:
  """Represents a single 3D printable brick configuration.

  A Brick encapsulates all parameters needed to generate an OpenSCAD file,
  including dimensions, type (Plate/Tile/Wall/Riser), features (studs, sockets,
  grid), and optional parameters like input STL files, rotations, textures, etc."""

  # Default values for optional brick parameters
  _DEFAULTS = {
    'rot': [0,0,0],          # Rotation angles [x, y, z]
    'input': '',             # Path to input STL file (for remix)
    'inputMin': [0,0,0],     # Minimum bounds of input mesh
    'inputMax': [0,0,0],     # Maximum bounds of input mesh
    'mirrorZ': 0.0,          # Z-axis mirror plane
    'bottomFill': 0.0,       # Bottom fill height
    'texture': '',           # Texture file path
    'cutX': -99,             # X-axis cutting plane
    'cutY': -99,             # Y-axis cutting plane
    'cutZ': -99,             # Z-axis cutting plane
  }


  def __init__(self, *,
               family='Square',
               set=None,
               size=None,
               type='Plate',
               variant=None,
               **kwds):
    """Initialize a Brick with configuration parameters.

    Args:
      family: Brick family (Square, Hex, HexR, HexS, Long, etc.)
      set: Name of the brick set this belongs to
      size: [x, y, z] dimensions in grid units
      type: Brick type (Plate, Tile, Wall, Riser)
      variant: Optional variant name for specialized versions
      **kwds: Additional parameters (rot, input, texture, etc.)
    """
    # Merge defaults with provided keyword arguments
    self._kwds = {**self._DEFAULTS, **kwds}
    self.family = family
    self.type = type
    self.set = set
    self.variant = variant
    self.size = size or [kwds.get('x', 0), kwds.get('y', 0), kwds.get('z', 0)]

    # Set type-specific defaults for studs, sockets, grid, and z-size
    match type:
      case 'Plate':
        # Standard plate: studs on top, sockets on bottom, internal grid
        self.studs = self._kwds.get('studs', True)
        self.sockets = self._kwds.get('sockets', True)
        self.grid = self._kwds.get('grid', True)
        self.size[2] = self.size[2] or 0.25
      case 'Tile':
        # Tile: smooth top (no studs), sockets on bottom, internal grid
        self.studs = self._kwds.get('studs', False)
        self.sockets = self._kwds.get('sockets', True)
        self.grid = self._kwds.get('grid', True)
        self.size[2] = self.size[2] or 0.25
      case 'Wall':
        # Wall: studs and sockets, no internal grid, tall
        self.studs = self._kwds.get('studs', True)
        self.sockets = self._kwds.get('sockets', True)
        self.grid = self._kwds.get('grid', False)
        self.size[2] = self.size[2] or 4.0
      case 'Riser':
        # Riser: studs and sockets, internal grid, 1 unit tall
        self.studs = self._kwds.get('studs', True)
        self.sockets = self._kwds.get('sockets', True)
        self.grid = self._kwds.get('grid', True)
        self.size[2] = self.size[2] or 1.0


  def __getattr__(self, key):
    """Allow accessing additional parameters as attributes.

    Args:
      key: Attribute name to retrieve

    Returns:
      The value from _kwds dictionary

    Raises:
      AttributeError: If key is not found in _kwds
    """
    try:
      if key[0].isalpha():
        return self._kwds[key]
    except KeyError:
      raise AttributeError(key)
    raise AttributeError(key)

  def scadConfigItems(self) -> Dict:
    """Generate OpenSCAD configuration parameters.

    Returns:
      Dictionary of configuration items formatted for OpenSCAD template expansion
    """
    def stringify(v):
      """Convert Python values to OpenSCAD string format."""
      if type(v) is bool:
        return "true" if v else "false"
      if type(v) is None:
        return "undef"
      return str(v)

    # Process all keywords, resolving texture names to paths
    kwds_processed = {}
    for k, v in self._kwds.items():
      if k == 'texture' and v:
        # Resolve texture name to file path
        kwds_processed[k] = resolve_texture_path(v)
      else:
        kwds_processed[k] = v

    # Return a defaultdict with all OpenSCAD parameters
    return collections.defaultdict(lambda: "undef",
      {'family': self.family,
      'studs': stringify(self.studs),
      'sockets': stringify(self.sockets),
      'grid': stringify(self.grid),
      'size': stringify(self.size),

      **{k: stringify(v) for (k,v) in kwds_processed.items()}
      }
    )

  @property
  def x(self) -> float:
    """Get the X dimension of the brick."""
    return self.size[0]

  @property
  def y(self) -> float:
    """Get the Y dimension of the brick."""
    return self.size[1]

  @property
  def z(self) -> float:
    """Get the Z dimension (height) of the brick."""
    return self.size[2]

  @property
  def name(self) -> str:
    """Generate a unique name for this brick.

    If 'name' is explicitly set in configuration, uses that.
    Otherwise, constructs a name from set, type, size, and variant.

    Returns:
      String name like 'SetName-Plate-2x4' or 'SetName-Plate-Hex3-VariantName'
    """
    if self._kwds.get('name', None):
      return self._kwds['name']

    # Format size string based on family type
    match self.family:
      case 'HexR' | 'HexS': sizeS = f'{self.family}{self.x}'
      case 'Hex': sizeS = f'{self.family}{self.x}x{self.y}'
      case 'Long': sizeS = f'{self.x}x{self.y}L'
      case _: sizeS = f'{self.x}x{self.y}'

    # Construct name from components
    name = (self.set, self.type, sizeS, self.variant)
    return '-'.join([str(n) for n in name if n is not None])

  @property
  def path(self) -> pathlib.Path:
    """Get the output path for this brick's OpenSCAD file.

    If 'path' is explicitly set in configuration, uses that.
    Otherwise, constructs path from set and type (e.g., 'SetName/Plates').

    Returns:
      pathlib.Path for the output directory
    """
    if self._kwds.get('path', None):
      return self._kwds['path']
    return pathlib.Path(self.set or '.', self.type + 's')

  def __str__(self) -> str:
    """String representation of the brick (returns its name)."""
    return self.name

