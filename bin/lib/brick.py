from __future__ import annotations

import pathlib

from absl import logging
from collections import UserDict
from typing import Any, Dict, Tuple

class InvalidBrick(ValueError):
  pass

class Brick(UserDict):
  _DEFAULTS = { 
      'family': 'Square',
      'subfamily': 'Tile',
      'set': 'Blank',
      'studs': False,
      'sockets': True,
      'grid': False,
      'size': None,
      'rot': (0, 0, 0),
      'input': '',
      'inputMin': (0, 0, 0),
      'inputMax': (0, 0, 0),
      'mirrorZ': 0.0,
      'bottomFill': 0.0,
      'texture': "",
      'name': None,
      'path': None,
  }

  def __init__(self, **kwds):
      self.data = {}
      for (k,v) in self._DEFAULTS.items():
        match k:
          case 'size':
            v = kwds.get(k, list((kwds.get('x'), kwds.get('y'), kwds.get('z'))))
          case 'name':
            v = kwds.get(k, self.name)
          case 'path':
            v = kwds.get(k, pathlib.Path(self.set, self.subfamily))
          case _: 
            v = kwds.get(k, v)
        if type(v) is tuple: v = list(v)
        self.data[k] = v

  def __getattr__(self, key):
    if key[0].isalpha():
      return self.data[key]
    raise KeyError(key)
    
  @property
  def config(self): 
    def stringify(v): 
      if type(v) is bool:
        return "true" if v else "false"
      return str(v)

    return {k:stringify(v) for (k,v) in self.data.items()} 

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
    if self.data.get('name', None):
      return self.data['name']
    if self.family in ('Hex-R', 'Hex-S'):
      name = [self.set, self.family, self.subfamily, self.x]
    else:
      name = [self.set, self.family, self.subfamily, f'{self.x:g}x{self.y:g}']
    return '-'.join([str(n) for n in name if n is not None])

  def __str__(self) -> str:
    return f'{self.name}'

