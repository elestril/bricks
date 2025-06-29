from __future__ import annotations

import collections
import copy
import functools
import pathlib
import stl
import regex as re


from typing import Dict, Iterator, Optional, Sequence
from absl import flags, logging

from lib.brick import Brick, InvalidBrick
from lib.globals import U
from lib.stats import STATS

flags.DEFINE_string('input', None, 'Base input directory.')
flags.DEFINE_multi_string('remix', [], '<remixconfig>:<fileglob> config and input stls to remix')
FLAGS = flags.FLAGS

class Remix:

  def __init__(self, name, config):

    if not FLAGS.input:
      raise ValueError(f'--input is not defined, nothing to remix')
    if FLAGS.remix and name not in self._remixes:
      raise ValueError(f'{name} not enabled in --remix: {FLAGS.remix}')

    self._glob = self._remixes.get(name) or pathlib.Path(FLAGS.input).glob('**/*.stl')
    self._regex = [re.compile(r) for r in config['regex']]
    self.name = name
    self.config = config['config']

  @functools.cached_property
  def _remixes(self): 
    return {
        conf: pathlib.Path(FLAGS.input).glob(glob) for (conf, glob) in [r.split(':', 1) for r in FLAGS.remix]
    }

  @functools.cached_property
  def _input(self):
    return pathlib.Path(FLAGS.input).resolve()

  @functools.cached_property
  def bricks(self) -> Iterator[Brick]:
    for infile in self._glob:
      logging.debug("remixing %s", infile)
      try:
        yield self._remix(infile)
      except InvalidBrick as e:
        logging.info('%s: cannot remix with config %s: %s ', infile.name, self.name, e)
        STATS[self.name]['invalid'] += 1


  def _remix(self, infile: pathlib.Path) -> Optional[Brick]:
    """Match a name to the regex and return a resolved config dict or None."""

    for match in [r.fullmatch(infile.name) for r in self._regex]:
      if match:
        logging.debug('%s: regex match %r', self.name, match.capturesdict())
        break
    else:
      raise InvalidBrick(f'{infile.name} does not match any regex')

    mesh = stl.Mesh.from_file(infile)
    vars = {
      'meshMin': mesh.min_.tolist(),
      'meshMax': mesh.max_.tolist(), 
      'meshDimension': [round(c) / 4 for c in ((mesh.max_ - mesh.min_) * 4.0 / U ).tolist()],
    }
    vars.update(((f'{k}', ''.join(v)) for (k,v) in match.capturesdict().items()))
    vars.update(((f'path{i}',v) for (i,v) in enumerate(infile.parts[:-5:-1])))

    brickConfig = {
      'name': infile.stem,
      'set': self.name,
      'input': infile.resolve(),
      'inputMin': copy.copy(vars['meshMin']),
      'inputMax': copy.copy(vars['meshMax']),
      'path': pathlib.Path(self.name, infile.parent.name.replace(' ', '')),
      'size': copy.copy(vars['meshDimension'])
    }
    
    
    for (group) in self.config:
      subconf = self.config[group]
      if group == '*': 
        brickConfig.update(subconf)
        continue

      matchgroups = group.split('/')
      # subkey = '/'.join([match.groupdict('')[g] for g in matchgroups])
      subkey = '/'.join([vars[g] for g in matchgroups])

      scval = subconf.get('*', {})
      if scval == False:
        raise InvalidBrick(f'{infile}: Config for {group}:{subkey} set to "False"') 
      brickConfig.update(scval)
        
      scval = subconf.get(subkey, subconf.get('_', {}))
      if scval == False:
        raise InvalidBrick(f'{infile}: Config for {group}:{subkey} set to "False"') 
      brickConfig.update(scval)

    vars['config'] = brickConfig
    logging.debug('Available variables for config expansion: %s', ', '.join([f'{var}="{val}"' for (var,val) in vars.items()]))
    for (k,v) in brickConfig.items():
      if type(v) is str:
        brickConfig[k] = v.format(**vars)

    logging.debug('Brick config: %r', brickConfig)
    brick = Brick(**brickConfig)
    logging.debug('Success: %s', brick)
    return brick


