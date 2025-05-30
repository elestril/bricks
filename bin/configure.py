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
from ruamel.yaml import YAML
from string import Template
from typing import Any, Optional, Dict, List


# MODULES = { 
#   'all': 'Configs for all bricks, plates, and tiles.',
#   'bricks': 'Create the standard bricks.',
#   'plates': 'Create the standard plates', 
#   'walls': 'Create the  standard walls',
#   'tiles': 'Create the standard tiles',
# }


FLAGS = flags.FLAGS
flags.DEFINE_string('remix_input', None, 'Path glob to input stl files')
flags.DEFINE_spaceseplist('config', None, 'Which configs to use.')

flags.DEFINE_string('confpath', str(pathlib.Path(__file__).parents[1].resolve().joinpath('configs')), 'Path to the yaml configs')

# flags.DEFINE_spaceseplist('modules', ['all'], 'Which modules to create:\n' + json.dumps(MODULES, indent=4))
# flags.register_validator('modules', lambda vals: all([val in MODULES for val in vals]), message=f'--module must be one or multiple of {MODULES.keys}')

flags.DEFINE_string('output', '.', 'Output directory or "-" for dumping config to stdout.')
flags.register_validator('output', lambda o: o == "-" or pathlib.Path(o).is_dir(), message='output must be "-" or an existing directory.')

flags.DEFINE_bool('individual_json', True, 'Write configs as individual files, one per stl file.')
flags.DEFINE_bool('combined_json', False, 'Write a single combined json config.')
flags.DEFINE_bool('rename', True, 'Create output stl files with a consistent nameing pattern. If false: Retain original stl filename')
flags.DEFINE_bool('makefile', True, "Create the Makefile(s)")


flags.DEFINE_integer('max_size', 8, 'Create bricks up to this size.')
flags.DEFINE_integer('max_r', 5, 'Create hex bricks up to radius r.')

CUSTOMIZER_TMPL = {
          'parameterSets': {},
          'fileFormatVersion': '1',
}

yaml = YAML()

#### Config ####

U = 12.7  # grid unit is 1/2in 

MAKEFILE_TMPL = """
include {includedMakefile}

"""

#### Code ####

class ConfigNotFound(KeyError):
  pass

class Brick:

  def __init__(self, **kwds):
    self.__dict__['_conf'] = { 
      'size': list((1,1,1))
    }
    self._conf.update(kwds)
    

  def __getattr__(self, attr) -> Any:
    match attr:
      case 'x': return self.size[0]
      case 'y': return self.size[1]
      case 'z': return self.size[2]
      case 'name': return self.getName()
      case 'stl': return self.getStl()
      case _: return self._conf.get(attr, None)
  
  def __setattr__(self, attr, val):
    match attr:
      case 'x': self.size[0] = val
      case 'y': self.size[1] = val
      case 'z': self.size[2] = val
      case _: self._conf[attr] = val

  def getName(self) -> str:
    if (self._name):
      return self._name

    if self.type in ('Hex-R', 'Hex-S'):
      ne = [self.set, self.label, f'{self.type}{self.x}']
    else:
      ne = [self.set, self.label, f'{self.x}x{self.y}']
    return '-'.join([str(n) for n in ne if n is not None])

  def getStl(self) -> pathlib.Path: 
    return pathlib.Path(self.set, self.subtype + 's').joinpath(self.name.__str__() + '.stl')

  def update(self, update: Dict):
    for (k,v) in update.items():
      setattr(self, k, v)

  def config(self): 
    return {
      k: v if type(v) in (int, float, str, bool) else str(v) for (k,v) in 
      self._conf.items()
    } 

  def isValid(self):
    return all(getattr(self, a) is not None for a in  ['type', 'subtype', 'label', 'x', 'y', 'z'])
        
    
class Config(object): 
  def __init__(self, yml: pathlib.Path): 
    y = yaml.load(yml)

    self.name = y['fileinfo']['name']
    self.tiles = y['fileinfo'].get('tiles', None)
    self.type = y['fileinfo']['type']

    if self.type == 'REMIX':
      self.regex = [re.compile(r) for r in y.get('regex', [])]
      self.config = y['config']
    else: 
      raise ValueError('%s: Unknown fileinfo.type %s', self.name, self.type)

  def match2Brick(self, filename) -> Optional[Brick]:
    """Match a name to the regex and return a resolved config dict or None."""

    file = pathlib.Path(filename)
    for match in [r.fullmatch(file.name) for r in self.regex]:
      if match:
        break
    else:
      return None

    def applyUpdate(brick: Brick, update: Dict, formatVars: Dict):
      if not update:
        return
      
    brick = Brick()
    brick.inputStl = file
    update = {}

    if '*' in self.config: 
      update.update(self.config['*'])
    for (group, matched) in match.groupdict().items():
      update.update(self.config[group].get('*', {}))
      update.update(self.config[group].get(matched, self.config[group].get('_', {})))
    
    for (k,v) in update.items():
        if type(v) is str:
          update[k] = v.vformat(match.groupdict())
        else:
          update[k] = v
    brick.update(update)
      
    log(DEBUG, '%s: match2Brick: %r', file, str(brick))
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

  if (FLAGS.individual_json): 
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

  if (FLAGS.combined_json):
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

  remix = []

  for yml in [pathlib.Path(FLAGS.confpath).joinpath(f'{c}.yaml') for c in FLAGS.config]:
    try:
      config = Config(yml)
    except Exception as e:
      log(WARNING, "%s: Error loading config: %r", yml, e)
      continue
    if config.name not in FLAGS.config:
      log(WARNING, 'Unexpected config %s, skipping.')
      continue
    if config.type == 'REMIX':
     remix.append(config)

  bricks = {}
  # bricks.update(generateBricks())

  # config = Config('rampage', regex=RAMPAGE_RE, conf=RAMPAGE_CONF)
  # log(DEBUG, 'input: %s', FLAGS.input)

  for infile in pathlib.Path('.').glob(FLAGS.remix_input): 
    for config in remix:
      brick = config.match2Brick(infile)
      if brick.isValid():
        bricks[brick.name] = brick
        break

  writeJsonConfigs(bricks)

if __name__ == '__main__':
  app.run(main)