#!/usr/bin/python3

import copy
import json
import numpy as np
import re
import shlex
import stl

import sys
import pathlib

from absl import app, flags
from absl.logging import log, WARNING, INFO, DEBUG
from string import Template
from typing import Optional, Dict, List


MODULES = { 
  'all': 'Configs for all bricks, plates, and tiles.',
  'bricks': 'Create the standard bricks.',
  'plates': 'Create the standard plates', 
  'walls': 'Create the  standard walls',
  'tiles': 'Create the standard tiles',
}


FLAGS = flags.FLAGS
flags.DEFINE_string('input', None, 'Path glob to input stl files')

flags.DEFINE_spaceseplist('modules', ['all'], 'Which modules to create:\n' + json.dumps(MODULES, indent=4))
flags.register_validator('modules', lambda vals: all([val in MODULES for val in vals]), message=f'--module must be one or multiple of {MODULES.keys}')

flags.DEFINE_string('output', '.', 'Output directory or "-" for dumping config to stdout.')
flags.register_validator('output', lambda o: o == "-" or pathlib.Path(o).is_dir(), message='output must be "-" or an existing directory.')

flags.DEFINE_bool('individual_configs', True, 'Write configs as individual files, one per stl file.')
flags.DEFINE_bool('combined_config', False, 'Write a single combined json config.')
flags.DEFINE_bool('rename', True, 'Create output stl files with a consistent nameing pattern. If false: Retain original stl filename')
flags.DEFINE_bool('makefile', True, "Create the Makefile(s)")
flags.DEFINE_integer('max_size', 8, 'Create bricks up to this size.')
flags.DEFINE_integer('max_r', 5, 'Create hex bricks up to radius r.')

CUSTOMIZER_TMPL = {
          'parameterSets': {},
          'fileFormatVersion': '1',
}

#### Config ####

U = 12.7  # grid unit is 1/2in 

RAMPAGE_RE = re.compile(r'(?P<code>\w+)(?:-(?P<kind>[A-Z]\w+))?(?:-(?P<set>[A-Z]\w+))?.*.stl')
GENERIC_RE = re.compile(r'(?P<name>.*).stl')

RAMPAGE_CONF = { 
  'code' : { 
    'A' : {'x': 4, 'y': 1},
    'AS': {'x': 4, 'y': 1},
    'E': {'x': 4, 'y': 4},
    'L': {'x': 1, 'y': 1},
  },
  'kind' : {
    'Window': {'type' : 'Brick', 'subtype': 'Wall', 'z': 4, 'mirrorZ': 7.2, 'label': '{kind}'},
    'Wall': {'type': 'Brick', 'subtype': 'Wall', 'z': 4, 'mirrorZ': 7.2, 'label': '{kind}'},
    'Column': {'type': 'Brick', 'subtype': 'Wall', 'z': 4, 'label': '{kind}{code}'},
    'Floor' : {'type': 'Brick', 'subtype': 'Tile', 'label': 'Tile', 'studs': False, 'z': 0.25, 'inputStlOffset': [0,0,-4.2]}
  },
  'set': { 
    'Schlist': {'set': 'Schist'},
    '*': {'set': '{set}'}
  }
}

MAKEFILE_TMPL = """
include {includedMakefile}

"""

#### Code ####

class ConfigNotFound(KeyError):
  pass

class Brick:

  def __init__(self, name = None, type = None, subtype = None, label = None, studs=None, sockets = True, 
               size = (4,1,4), grid = None, inputStl = None, inputStlOffset=(0,0,0), mirrorZ=0):
    self._name = name
    self.type = type
    self.subtype = subtype
    self.label = label
    self.studs = studs 
    self.sockets = sockets
    self.size  = list(size)
    self.grid = grid
    self.inputStl = inputStl
    self.inputStlOffset = list(inputStlOffset)
    self.mirrorZ = mirrorZ

  @property
  def name(self) -> str:
    if (self._name):
      return self._name

    if self.type in ('Hex-R', 'Hex-S'):
      ne = [self.set, self.label, f'{self.type}{self.x}']
    else:
      ne = [self.set, self.label, f'{self.x}x{self.y}']
    return '-'.join([str(n) for n in ne if n is not None])

  @property
  def stl(self) -> pathlib.Path: 
    return pathlib.Path(self.set, self.subtype + 's').joinpath(self.name.__str__() + '.stl')

  @property
  def x(self): 
    return self.size[0]

  @property
  def y(self): 
    return self.size[1]

  @property
  def z(self): 
    return self.size[2]

  @x.setter
  def x(self, val) -> None:
    self.size[0] = val

  @y.setter
  def y(self, val) -> None:
    self.size[1] = val

  @z.setter
  def z(self, val) -> None:
    self.size[2] = val

  def update(self, update: Dict):
    for (k,v) in update.items():
      setattr(self, k, v)

  def config(self): 
    return {
      k: v if type(v) in (int, float, str, bool) else str(v) for (k,v) in 
        {attr: getattr(self, attr) for attr in 
          ('name', 'type', 'subtype', 'label', 'studs', 'sockets', 'grid', 'size', 'inputStl', 'inputStlOffset', 'mirrorZ') 
        }.items() 
      if v is not None
    } 

  def validate(self):
    errors = []
    for a in ['type', 'subtype', 'label']:
      if getattr(self, a) is None: 
        errors.append(a)
    if errors: 
      raise KeyError(f'{self.name}: Attributes not configured: {errors}')
        
    
class Config(object): 
  def __init__(self, name, *, regex: re.Pattern  = None, pathT: str = None, conf: Dict = None):
    self.name = name
    self.regex = regex
    self.pathT = pathT
    self.conf = conf

  def match2Brick(self, filename) -> Optional[Brick]:
    """Match a name to the regex and return a resolved config dict or None."""

    file = pathlib.Path(filename)
    match = self.regex.fullmatch(file.name)
    if not match:
      return None

    log(DEBUG, '%s match: %r', file.name, match.groupdict())

    brick = Brick()
    brick.inputStl = file
    for (group, matched) in match.groupdict().items():
      update = copy.deepcopy(self.conf[group].get(matched, self.conf[group].get('*', None)))
      if update is None:
        continue
      for (k,v) in update.items():
        if type(v) is str:
          update[k] = v.format(**match.groupdict())
      log(DEBUG, '%s: Update for group %s:%s %r', file.name, group, matched, update)
      brick.update(update)

    log(DEBUG, '%s: match2Brick: %r', file, str(brick))
    brick.validate()
    return brick
  
def generateBricks() -> Dict: 

  s = FLAGS.max_size + 1
  r = FLAGS.max_r + 1
  configs = {} 

  if 'all' in FLAGS.modules or 'plates' in FLAGS.modules:
    configs.update({
      b.name:b for b in [
        Brick(x, y, 0.25, type='Brick', subtype='Plate') for x in range(1,s) for y in range(1,s) if x>=y]
    })
    configs.update({
      b.name: b for b in [
        Brick(x, 0, 0.25, type=type, subtype='Plate') for x in range(1,r) for type in ('Hex-R', 'Hex-S')] 
    })
  if 'all' in FLAGS.modules or 'tiles' in FLAGS.modules:
    configs.update({
      b.name:b for b in [
        Brick(x, y, 0.25, type='Brick', subtype='Tile') for x in range(1,s) for y in range(1,s) if x>=y]
    })
    configs.update({
      b.name: b for b in [
        Brick(x, 0, 0.25, type=type, subtype='Tile') for x in range(1,r) for type in ('Hex-R', 'Hex-S')] 
    })
  if 'all' in FLAGS.modules or 'walls' in FLAGS.modules:
    configs.update({
      b.name:b for b in [Brick(x, 1, 4, type='Brick', subtype='Wall') for x in range(1,s)]
    })
    configs.update({
      b.name:b for b in [Brick(x, 1, 2, type='Brick', subtype='LowWall') for x in range(1,s)]
    })
  return configs


def writeJsonConfigs(bricks):
  if FLAGS.output == '-': 
    conf = copy.deepcopy(CUSTOMIZER_TMPL)
    conf['parameterSets'] = {n: b.config for (n,b) in bricks.items()}
    json.dump(conf, sys.stdout, indent=2, sort_keys=True)
    return

  outpath = pathlib.Path(FLAGS.output)
  if not outpath.is_dir():
    raise FileNotFoundError('%s must be a directory.')
  
  outpaths = set((outpath,))
  includedMakefile = pathlib.Path(__file__).parents[1].joinpath('Makefile.mk').resolve()

  if (FLAGS.individual_configs): 
    for (name, brick) in bricks.items():

      conf = brick.config()
      conf['stl'] = brick.stl.name
      conf['inputStl'] = str(brick.inputStl.resolve())

      jf = brick.stl.parent.joinpath(brick.stl.stem + '.json')

      outpaths.update(list(brick.stl.parents))

      log(DEBUG, '%s: %r', name, conf)
      try: 
        with open(jf, 'r') as jfd:
          oldConf = json.load(jfd)
      except: 
        oldConf = {}
      if (oldConf.get('parameterSets', {}).get(name, {}) == conf):
        log(INFO, '%s: No changes, skipping updates.', name)
        continue

      cconf = copy.deepcopy(CUSTOMIZER_TMPL)
      cconf['parameterSets'][name] = conf
      
      log(INFO, '%s: writing config %r', name, cconf)
      jf.parent.mkdir(parents=True, exist_ok=True)
      with open(jf, 'w') as jfd:
        json.dump(cconf, jfd, indent=2, sort_keys=True)

  if (FLAGS.combined_config):
    cconf = copy.deepcopy(CUSTOMIZER_TMPL)
    cconf['parameterSets'] = {n:b.config for (n,b) in bricks.items()}
    with open(outpath.joinpath('configs.json')) as jfd:
        json.dump(cconf, jfd, indent=2, sort_keys= True)

  if FLAGS.makefile: 
    for op in outpaths:
      inclMake = includedMakefile.relative_to(op.resolve(), walk_up=True)
      with open(op.joinpath("Makefile"), "w") as out:
        out.write(MAKEFILE_TMPL.format(includedMakefile=inclMake))

def main(argv): 
  del argv

  output = pathlib.Path(FLAGS.output)

  bricks = {}
  bricks.update(generateBricks())

  config = Config('rampage', regex=RAMPAGE_RE, conf=RAMPAGE_CONF)
  
  log(DEBUG, 'input: %s', FLAGS.input)

  for infile in pathlib.Path('.').glob(FLAGS.input): 
    try:
      brick = config.match2Brick(infile)
      bricks[brick.name] = brick
    except Exception as e:
      log(WARNING, "%s: Skipping. %s", infile, e)

  writeJsonConfigs(bricks)

if __name__ == '__main__':
  app.run(main)