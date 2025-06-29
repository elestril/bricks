from __future__ import annotations

import collections
import copy
import json
import mergedeep
import pathlib
import sys

from absl import flags, logging
from ruamel.yaml import YAML
from typing import Any, Optional, Dict, Sequence, Iterator, Tuple

from lib.remix import Remix
from lib.generate import Generate
from lib.brick import Brick
from lib.globals import BASEDIR, scadpath
from lib.stats import STATS

flags.DEFINE_string('output', '.', 'Outpot directory.')
flags.register_validator('output', lambda o: pathlib.Path(o).is_dir(), message='output must be an existing directory.')

flags.DEFINE_bool('scad_output', True, 'Write configs as individual scad files, one per stl file.')
FLAGS = flags.FLAGS

yaml = YAML()

U = 12.7  # grid unit is 1/2in 

MAKEFILE_TMPL = """
include {incl}

"""


class Bricks: 
  """All known bricks.

  Attributes: 
    * config: Dict resulting from merging all yaml configs
    * bricksets: All 'BrickSet' classes configured in config.
    * bricks: All Bricks, by name
  """

  def __init__(self):
    self.bricksets: Dict[str, BrickSet] = dict()
    self._bricks: Dict[str, Brick] = dict() 

    self.outpaths = set()
    logging.debug('remix: %r', FLAGS.remix)
    self.generates = {
      conf:True for conf in FLAGS.generate
    }


  def configure(self, ymls: Sequence[pathlib.Path]): 
    for yml in [yaml.load(yml.read_text()) for yml in ymls]:
      for (name, conf) in yml.get('generate', {}).items():
        try:
          self.add_brickset(Generate(name, conf))
        except ValueError as e:
          logging.info(e)
          continue

      for (name, conf) in yml.get('remix', {}).items():
        try:
          self.add_brickset(Remix(name, conf))
        except ValueError as e:
          logging.info(e)
          continue
      
  def add_brickset(self, brickset: BrickSet):
    if brickset.name in self.bricksets:
      raise KeyError('Duplicate brickset "{brickset.name}"')
    self.bricksets[brickset.name] = brickset


  def bricks(self) -> Iterator[Brick]:
    for brickset in self.bricksets.values():
      yield from brickset.bricks


  def writeConfigs(self):
    global STATS

    with open(scadpath().joinpath('brick.template.scad')) as tmpl:
      scadTemplate = tmpl.read()

    output = pathlib.Path(FLAGS.output)
    if not output.is_dir():
      raise FileNotFoundError('%s must be a directory.')

    if not output.joinpath('Makefile').exists():
      with open(output.joinpath('Makefile'), 'w') as fd:
        fd.write(MAKEFILE_TMPL.format(incl=BASEDIR.joinpath('Makefile.mk').resolve().relative_to(output.resolve(), walk_up=True)))


    jsonConfigPath = pathlib.Path(output).joinpath('config.json')
    jsonConfig = {}
    if jsonConfigPath.exists():
      with open(jsonConfigPath, 'r') as jfd:
        jsonConfig = json.load(jfd).get('parameterSets', {})

    for brick in self.bricks():

      logging.debug('%s/%s: %r', brick.path, brick.name, brick.config)

      scadFile = output.joinpath(brick.path, brick.name + '.scad').resolve()

      if brick.config == jsonConfig.get(brick.name, {}) and scadFile.exists():
        STATS[brick.set]['unchanged'] += 1
        STATS['total']['unchanged'] += 1
        logging.info(f'{brick.name}: Unchanged')
        continue

      jsonConfig[brick.name] = brick.config
      scadConfig = scadTemplate.format(**brick.config)

      if not scadFile.parent.exists():
        scadFile.parent.mkdir(parents=True)    
        with open(scadFile.parent.joinpath("Makefile"), "w") as out:
          out.write(MAKEFILE_TMPL.format(incl=BASEDIR.joinpath('Makefile.mk').resolve().relative_to(scadFile, walk_up=True).name))

      if scadFile.exists():
        neworupdate = 'updated'
      else:
        neworupdate = 'new'

      with open(scadFile, 'w') as fd:
        fd.write(scadConfig)
        STATS[brick.set][neworupdate] += 1
        STATS['total'][neworupdate] += 1

    with open(jsonConfigPath, 'w') as fd:
      json.dump(
        {'parameterSets': jsonConfig,
        'fileFormatVersion': '1',
      }, fd, indent=2)

  def __str__(self): 
    return self.name
