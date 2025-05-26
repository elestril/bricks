#!/usr/bin/python3

import copy
import glob
import json
import numpy as np
import re
import shlex
import stl
import sys
import pathlib

from absl import app, flags
from absl.logging import log, WARNING, INFO, DEBUG
from typing import Optional, Dict, List


MODULES = { 
  'all': 'Configs for all bricks, plates, and tiles.',
  'bricks': 'Create the standard bricks.',
  'plates': 'Create the standard plates', 
  'walls': 'Create the  standard walls',
  'tiles': 'Create the standard tiles',
  'textures': 'Turn the input files into textures', 
  'remix': 'Remix the input files into Dungeonbricks', 
}


FLAGS = flags.FLAGS
flags.DEFINE_spaceseplist('input', None, 'Path(s) to input stl files')
flags.DEFINE_bool('recursive', False, 'Whether to create a recursive hierarchy of json files')

flags.DEFINE_spaceseplist('modules', 'all', 'Which modules to create:\n' + json.dumps(MODULES, indent=4))
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

RAMPAGE_RE = re.compile(r'(?P<name>(?P<code>\w+)(-(?P<kind>[A-Z]\w+))?(-(?P<set>[A-Z]\w+))?.*).stl')
GENERIC_RE = re.compile(r'(?P<name>.*).stl')

OPENLOCK_CONFIG_TMPL = { 
  '*': { 
    '*':  {'type': 'Wall', 'studs': True, 'sockets': True, 'mirrorZ': 7.2},
    'A':  {'size': [4, 1, 4]},
    'AS': {'size': [4, 1, 4]},
    'L': {'size': [1, 1, 4]},
  },
  'Floor': { 
    '*':  {'type': 'Tile', 'studs': False, 'sockets': True},
    'E': {'size': [4,4,0.25]},
  },
  'Roof': None,
  'RoofEnd': None,
}

MAKEFILE_TMPL = """
include {includedMakefile}

"""

#### Code ####


class ConfigNotFound(KeyError):
  pass


class Brick(object): 
  def __init__(self, size, cls='Brick', type='Wall', subtype=None, set='Blank', name=None):
    self.cls = cls
    self.type = type
    self.subtype = subtype
    self.set = set
    self.size = list(size)
    self._name = None

  @property
  def name(self):
    if (self._name):
      return self._name

    if self.cls in ('Hex-R', 'Hex-S'):
      ne = [self.set, self.type, self.subtype, f'{self.cls}{self.x}']
    else:
      ne = [self.set, self.type, self.subtype, f'{self.x}x{self.y}']
    return '-'.join([str(n) for n in ne if n is not None])

  @property
  def x(self): 
    return self.size[0]
  
  @property
  def y(self): 
    return self.size[1]
  
  @property
  def z(self):
    return self.size[2]

  @property
  def stl(self): 
    return pathlib.Path(self.set, self.type + 's').joinpath(self.name + '.stl')

  @property
  def studs(self): 
    return self.type != 'Tile'

  @property
  def config(self): 
    return { 
      'class': self.cls, 
      'type': self.type, 
      'subtype': self.subtype,
      'set': self.set,
      'name': self.name,
      'size': str(self.size),
      'stl': str(self.stl),
      'studs': self.studs,
    }


def generateBricks() -> Dict: 

  s = FLAGS.max_size + 1
  r = FLAGS.max_r + 1
  configs = {} 

  if 'all' in FLAGS.modules or 'plates' in FLAGS.modules:
    configs.update({
      b.name:b for b in [
        Brick((x, y, 0.25), type='Plate') for x in range(1,s) for y in range(1,s) if x>=y]
    })
    configs.update({
      b.name: b for b in [
        Brick((x, 0, 0.25), type='Plate', cls=cls) for x in range(1,r) for cls in ('Hex-R', 'Hex-S')] 
    })
  if 'all' in FLAGS.modules or 'tiles' in FLAGS.modules:
    configs.update({
      b.name:b for b in [
        Brick((x, y, 0.25), type='Tile') for x in range(1,s) for y in range(1,s) if x>=y]
    })
    configs.update({
      b.name: b for b in [
        Brick((x, 0, 0.25), type='Tile', cls=cls) for x in range(1,r) for cls in ('Hex-R', 'Hex-S')] 
    })
  if 'all' in FLAGS.modules or 'walls' in FLAGS.modules:
    configs.update({
      b.name:b for b in [Brick((x, 1, 4), type='Wall') for x in range(1,s)]
    })
    configs.update({
      b.name:b for b in [Brick((x, 1, 2), type='LowWall') for x in range(1,s)]
    })
  return configs


def tmpl2Conf(template: Dict, info: Dict) -> Optional[Dict]: 
  """Lookup config in template.
  
  raises: KeyError when no matching config exists.

  """
  config = {}
  config['kind'] = info['kind']

  tmpl = template.get(info['kind'], template['*'])
  if not tmpl: 
    raise ConfigNotFound(info['kind'])

  try:
    config.update(tmpl['*'])
    config.update(tmpl[info['code']])
  except KeyError as e:
    raise ConfigNotFound(str(e))

  log(DEBUG, 'tmpl2conf: %r %r', template, config)
  return config

def stl2Config(filename: str) -> Optional[Dict]:
  'Produce an scad customizer json file from an stl to parametrize the remix.'

  filepath = pathlib.Path(filename).resolve()
  basename = pathlib.Path(filename).name

  conf = {'inputStl': str(filepath)}

  if match := RAMPAGE_RE.fullmatch(basename):
    conf['set'] = match.group('set')
    fromTmpl = tmpl2Conf(OPENLOCK_CONFIG_TMPL, match.groupdict())
    log(DEBUG, "fromTmpl: %r", fromTmpl)
    conf.update(fromTmpl)
  elif match := GENERIC_RE.fullmatch(basename): 
    conf['kind'] = None
    conf['set'] = None
  else: 
    raise KeyError('not matching any known pattern')

  msh = stl.mesh.Mesh.from_file(filename)

  inputStlOffset = msh.min_
  if (conf['type'] == 'Tile'):
    inputStlOffset[2] = -msh.max_[2] + 4.0
  conf['inputStlOffset'] = [round(v,2) for v in inputStlOffset.tolist()]

  stlSize = np.round(((msh.max_ - msh.min_) * 2 / U )/ 2).tolist()

  # if (stlSize != conf['size']):
  #   raise ConfigNotFound('Size of stl %r differs from template size %r', stlSize, conf['size'])

  if FLAGS.rename:
    conf['name'] = f"{conf['kind']}-{conf['set']}-{conf['size'][0]}x{conf['size'][1]}"
  else:
    conf['name'] = basename.split()[0]

  conf['stl'] = conf['name'] + '.stl'
  return conf


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
      conf = brick.config
      conf['stl'] = brick.stl.name
      jf = brick.stl.parent.joinpath(brick.stl.stem + '.json')

      outpaths.update(brick.stl.parents[:])

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
      
      log(DEBUG, '%s: writing config %r', name, cconf)
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

def main(argv: List[str]): 
  input = argv[1:]

  output = pathlib.Path(FLAGS.output)

  bricks = {}
  bricks.update(generateBricks())
  writeJsonConfigs(bricks)

  return

  for stlfile in input:
    stlParams = {
          'parameterSets': {},
          'fileFormatVersion': '1',
        }
    try:  
      conf = stl2Config(stlfile)
    except ConfigNotFound as e:
      log(WARNING, '%s: No matching config in template: %s', stlfile, e)
      continue

    # scad customizer expects vectors as string represenation.
    for (k,v) in conf.items():
      if isinstance(v, list) :
        conf[k] = repr(v)
    stlParams['parameterSets'][conf['name']] = conf
    params['parameterSets'][conf['name']] = conf
    if (FLAGS.individual_configs): 
      with open(output.joinpath(conf['name'] + '.json'), 'w') as out:
        json.dump(stlParams, out, indent=2, sort_keys=True)
        log(INFO, '%s: SUCCESS %s', stlfile, out.name)
    
  confJ = json.dumps(params, indent=2, sort_keys=True)
  log(DEBUG, confJ)

  if (FLAGS.combined_config):
    with open(output.joinpath('config.json'), 'w') as out:
      out.write(confJ)

  

if __name__ == '__main__':
  app.run(main)