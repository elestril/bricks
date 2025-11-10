from __future__ import annotations

import collections
import pathlib

from absl import logging
from collections import UserDict
from typing import Any, Dict, Tuple

class InvalidBrick(ValueError):
  pass

class Brick:

  _DEFAULTS = { 
    'rot': [0,0,0],
    'input': '',
    'inputMin': [0,0,0],
    'inputMax': [0,0,0],
    'mirrorZ': 0.0,
    'bottomFill': 0.0,
    'texture': '',
    'cutX': -99,
    'cutY': -99,
    'cutZ': -99,
  }


  def __init__(self, *,
               family='Square',
               set=None,
               size=None,
               type='Plate',
               variant=None,
               **kwds):

      self._kwds = {**self._DEFAULTS, **kwds}
      self.family = family
      self.type = type
      self.set = set
      self.variant = variant
      self.size = size or [kwds.get('x', 0), kwds.get('y', 0), kwds.get('z', 0)]
      match type:
        case 'Plate':
          self.studs = self._kwds.get('studs', True)
          self.sockets = self._kwds.get('sockets', True)
          self.grid = self._kwds.get('grid', True)
          self.size[2] = self.size[2] or 0.25
        case 'Tile':
          self.studs = self._kwds.get('studs', False)
          self.sockets = self._kwds.get('sockets', True)
          self.grid = self._kwds.get('grid', True)
          self.size[2] = self.size[2] or 0.25
        case 'Wall':
          self.studs = self._kwds.get('studs', True)
          self.sockets = self._kwds.get('sockets', True)
          self.grid = self._kwds.get('grid', False)
          self.size[2] = self.size[2] or 4.0
        case 'Riser':
          self.studs = self._kwds.get('studs', True)
          self.sockets = self._kwds.get('sockets', True)
          self.grid = self._kwds.get('grid', True)
          self.size[2] = self.size[2] or 1.0


  def __getattr__(self, key):
    try:
      if key[0].isalpha():
        return self._kwds[key]
    except KeyError:
      raise AttributeError(key)
    raise AttributeError(key)
    
  def scadConfigItems(self) -> Dict: 
    def stringify(v): 
      if type(v) is bool:
        return "true" if v else "false"
      if type(v) is None:
        return "undef"
      return str(v)

    return collections.defaultdict(lambda: "undef", 
      {'family': self.family,
      'studs': stringify(self.studs),
      'sockets': stringify(self.sockets),
      'grid': stringify(self.grid),
      'size': stringify(self.size),

      **{k: stringify(v) for (k,v) in self._kwds.items()}
      }
    )

  @property
  def x(self) -> float:
    return self.size[0]

  @property
  def y(self) -> float:
    return self.size[1]

  @property
  def z(self) -> float:
    return self.size[2]

  @property
  def name(self) -> str:
    if self._kwds.get('name', None):
      return self._kwds['name']
    
    match self.family:
      case 'HexR' | 'HexS': sizeS = f'{self.family}{self.x}'
      case 'Hex': sizeS = f'{self.family}{self.x}x{self.y}'
      case 'Long': sizeS = f'{self.x}x{self.y}L'
      case _: sizeS = f'{self.x}x{self.y}'

    name = (self.set, self.type, sizeS, self.variant)
    return '-'.join([str(n) for n in name if n is not None])

  @property
  def path(self) -> pathlib.Path:
    if self._kwds.get('path', None):
      return self._kwds['path']
    return pathlib.Path(self.set or '.', self.type + 's')

  def __str__(self) -> str:
    return self.name

