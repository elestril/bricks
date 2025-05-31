#!/usr/bin/python3

import collections
import datetime
import copy
import json
import numpy as np
import regex as re
import logging as pylogging
import shlex
import stl
import io

import sys
import pathlib

from absl import app, flags, logging
from ruamel.yaml import YAML
from string import Template
from typing import Any, Optional, Dict, List

FLAGS = flags.FLAGS
flags.DEFINE_string('remix_input', None, 'Path glob to input stl files')
flags.DEFINE_spaceseplist('config', None, 'Which configs to use.')

flags.DEFINE_string('confpath', str(pathlib.Path(__file__).parents[1].resolve().joinpath('configs')), 'Path to the yaml configs')
flags.DEFINE_string('scadpath', str(pathlib.Path(__file__).parents[1].resolve().joinpath('scad')), 'Path to the scad files')

flags.DEFINE_string('output', '.', 'Output directory or "-" for dumping config to stdout.')
flags.register_validator('output', lambda o: o == "-" or pathlib.Path(o).is_dir(), message='output must be "-" or an existing directory.')
flags.DEFINE_string('logfile', 'configure.log', 'Location of the logfile')

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
SCADPATH = None
STATS=collections.defaultdict(collections.Counter)

#### Config ####

U = 12.7  # grid unit is 1/2in 

MAKEFILE_TMPL = """
include {includedMakefile}

"""

#### Code ####


class InvalidBrick(ValueError):
  pass

class FormatDict(collections.OrderedDict): 
  def __getattr__(self, attr):
    if attr in self:
      return self.__getitem__(attr)
    else: 
      return ''

class Brick:
  # These need to be set for the brick to be valid.
  REQUIRED_FIELDS = ('name', 'type', 'subtype', 'label', 'set', 'x', 'y', 'z')

  def __init__(self, **kwds):
    self.__dict__['_conf'] = { 
      'size': list((None, None, None))
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
      ne = [self.set, self.label, f'{self.x:g}x{self.y:g}']
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

  def validate(self):
    missing = [k for k in self.REQUIRED_FIELDS if not getattr(self, k)]
    if missing:
      raise InvalidBrick(f'{self.name}: Missing fields: {missing}')
    return True

    
class Config(object): 
  def __init__(self, yml: pathlib.Path): 
    y = yaml.load(yml)
    self.name = yml.stem
    self.type = y['fileinfo']['type']

    if self.type == 'REMIX':
      self.regex = [re.compile(r) for r in y.get('regex', [])]
      self.config = y['config']
    else: 
      raise ValueError('%s: Unknown fileinfo.type %s', self.name, self.type)

  def remix(self, filename) -> Optional[Brick]:
    """Match a name to the regex and return a resolved config dict or None."""

    file = pathlib.Path(filename)
    for match in [r.fullmatch(file.name) for r in self.regex]:
      if match:
        logging.debug('regex match: %r', match.capturesdict())
        logging.debug('regex match: %r', match.groups())
        break
    else:
      raise InvalidBrick(f'{file.name} does not match any regex')

    brick = Brick()
    brick.inputStl = file


    mesh = stl.Mesh.from_file(file)
    
    meshinfo = { 
      'inputStlMin': mesh.min_.tolist(),
      'inputStlMax': mesh.max_.tolist(), 
      'size': [round(c) / 4 for c in ((mesh.max_ - mesh.min_) * 4.0 / U ).tolist()],
    }
    vars = {} 
    vars.update(((f'{k}',v) for (k,v) in meshinfo.items()))
    vars.update(((f'{k}', ''.join(v)) for (k,v) in match.capturesdict().items()))
    vars.update(((f'path{i}',v) for (i,v) in enumerate(file.parts[:-5:-1])))

    bupdate = collections.OrderedDict(meshinfo)

    for (group) in self.config:
      subconf = self.config[group]
      if group == '*': 
        bupdate.update(subconf)
        continue

      matchgroups = group.split('/')
      # subkey = '/'.join([match.groupdict('')[g] for g in matchgroups])
      subkey = '/'.join([vars[g] for g in matchgroups])

      scval = subconf.get('*', {})
      if scval == False:
        raise InvalidBrick(f'{file}: Config for {group}:{subkey} set to "False"') 
      bupdate.update(scval)
        
      scval = subconf.get(subkey, subconf.get('_', {}))
      if scval == False:
        raise InvalidBrick(f'{file}: Config for {group}:{subkey} set to "False"') 
      bupdate.update(scval)

      logging.debug(f'group:{group} subkey:{subkey}')

    vars['config'] = FormatDict(bupdate)
    logging.debug('Available variables for config expansion: %s', ', '.join([f'{var}="{val}"' for (var,val) in vars.items()]))
    for (k,v) in bupdate.items():
      if type(v) is str:
        bupdate[k] = v.format(**vars)

    brick.update(bupdate)
    brick.validate()
    return brick

  def __str__(self): 
    return self.name
  
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
  global STATS

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
      conf['inputStl'] = str(brick.inputStl.resolve().relative_to(SCADPATH, walk_up=True))

      jf = brick.stl.parent.joinpath(brick.stl.stem + '.json')

      outpaths.update(list(brick.stl.parents))

      try: 
        with open(jf, 'r') as jfd:
          oldConf = json.load(jfd)
      except: 
        oldConf = {}
      if (oldConf.get('parameterSets', {}).get(name, {}) == conf):
        logging.info(f'{jf}: No changes')
        STATS[brick.set]['unchanged'] += 1
        continue

      cconf = copy.deepcopy(CUSTOMIZER_TMPL)
      cconf['parameterSets'][name] = conf
      
      logging.info(f'{jf}: Updated')
      jf.parent.mkdir(parents=True, exist_ok=True)
      with open(jf, 'w') as jfd:
        STATS[brick.set]['written'] += 1
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
  global SCADPATH
  global STATS

  SCADPATH = pathlib.Path(FLAGS.scadpath).resolve()

  output = pathlib.Path(FLAGS.output)

  logging.get_absl_handler().setFormatter(pylogging.Formatter(
    fmt=None
  ))
  remix = []
  logging.info(f'{datetime.datetime.now().isoformat()}: {" ".join(sys.argv)}')

  for yml in [pathlib.Path(FLAGS.confpath).joinpath(f'{c}.yaml') for c in FLAGS.config]:
    try:
      config = Config(yml)
    except Exception as e:
      logging.warning("%s: Error loading config: %r", yml, e)
      continue
    if config.name not in FLAGS.config:
      logging.warning('Unexpected config %s, skipping.')
      continue
    if config.type == 'REMIX':
     remix.append(config)

  bricks = {}

  for infile in pathlib.Path('.').glob(FLAGS.remix_input): 
    logging.debug("remixing %s", infile)
    for config in remix:
      try:
        brick = config.remix(infile)
        logging.info('%s: remixing as %s, config %s. %s', infile.name, brick.name, config.name, brick.config() if logging.level_debug() else '')
        if brick.name in bricks:
          logging.warning("%s: Brick %s already exists, ignoring", infile, brick.name)
          STATS[config]['duplicate'] += 1
        else:
          bricks[brick.name] = brick
          STATS[config]['valid'] += 1
        break
      except InvalidBrick as e:
        logging.info('%s: cannot remix with config %s: %s ', infile.name, config.name, e)
        STATS[config]['invalid'] += 1

  writeJsonConfigs(bricks)

  with io.StringIO() as ybuf:
    yaml.dump({str(k): dict(v) for (k,v) in STATS.items()}, ybuf)
    logging.info('\n\n**** STATS ****\n\n%s', ybuf.getvalue())

if __name__ == '__main__':
  app.run(main)