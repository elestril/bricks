#!/usr/bin/python3

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


FLAGS = flags.FLAGS
flags.DEFINE_bool('recursive', False, 'Whether to create a recursive hierarchy of json files')
flags.DEFINE_string('output', './', 'Output directory')
flags.DEFINE_bool('individual_configs', True, 'Write configs as individual files, one per stl file')
flags.DEFINE_bool('combined_config', False, 'Write configs in a single combined json config.')
flags.DEFINE_bool('rename', True, 'Create output stl files with a consistent nameing pattern. If false: Retain original stl filename')
flags.DEFINE_bool('makefile', True, "Create a Makefile(s)")

#### Config ####

U = 12.7  # grid unit is 1/2in 

RAMPAGE_RE = re.compile(r'(?P<name>(?P<code>\w+)-(?P<type>\w+)-(?P<set>\w+).*).stl')
GENERIC_RE = re.compile(r'(?P<name>.*).stl')

STL_NAME_TMPL = "{kind}-{set}-{size[0]}x{size[1]}"

OPENLOCK_CONFIG_TMPL = { 
  'Wall': { 
    '*':  {'kind': 'Wall', 'studs': True, 'sockets': True, 'mirrorZ': 7.0},
    'A':  {'size': [4, 1, 4]},
    'AS': {'size': [4, 1, 4]},
    'L': {'size': [1, 1, 4]},
  },
  'Floor': { 
    '*':  {'kind': 'Tile', 'studs': False, 'sockets': True},
    'E': {'size': [4,4,0.25]},
  },
}
OPENLOCK_CONFIG_TMPL['Column'] = OPENLOCK_CONFIG_TMPL['Wall']

MAKEFILE_TMPL = """
include {includedMakefile}

stl: {stls}

configs: {configs}

{configs} &: {configDepends}
\t{configure}

"""

#### Code ####

def tmpl2Conf(template: Dict, info: Dict) -> Optional[Dict]: 
  """Lookup config in template.
  
  raises: KeyError when no matching config exists.

  """
  config = {}
  config.update(template[info['type']]['*'])
  config.update(template[info['type']][info['code']])

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
    conf.update(fromTmpl)
  elif match := GENERIC_RE.fullmatch(basename): 
    conf['kind'] = 'generic'
    conf['set'] = 'generic'
  else: 
    raise KeyError('not matching any known pattern')

  msh = stl.mesh.Mesh.from_file(filename)


  inputStlOffset = msh.min_

  if (conf['kind'] == 'Tile'):
    inputStlOffset[2] = -msh.max_[2] + 0.25*U
  conf['inputStlOffset'] = [round(v,2) for v in inputStlOffset.tolist()]

  if 'size' not in conf:
    conf['size'] = np.round(((msh.max_ - msh.min_) * 2 / U )/ 2).tolist()

  if FLAGS.rename:
    conf['name'] = STL_NAME_TMPL.format(**conf) 
  else:
    conf['name'] = basename.split()[0]

  conf['stl'] = conf['name'] + '.stl'
  return conf


def main(argv: List[str]): 
  input = argv[1:]

  output = pathlib.Path(FLAGS.output)

  params ={
          'parameterSets': {},
          'fileFormatVersion': '1',
        }

  for stlfile in input:
    stlParams = {
          'parameterSets': {},
          'fileFormatVersion': '1',
        }
    try:  
      conf = stl2Config(stlfile)
    except KeyError as e:
      log(WARNING, "%s: No config found in template, missing entry: %s", stlfile, e)
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
        log(INFO, 'SUCCESS: %s', out.name)
    

  confJ = json.dumps(params, indent=2, sort_keys=True)
  log(DEBUG, confJ)

  if (FLAGS.combined_config):
    with open(output.joinpath('config.json'), 'w') as out:
      out.write(confJ)

  
  if FLAGS.makefile: 
    includedMakefile = pathlib.Path(__file__).parents[1].joinpath('stl', 'Makefile.mk').relative_to(output.absolute(), walk_up=True)
    stls = ' '.join([shlex.quote(conf['stl']) for conf in params['parameterSets'].values()])
    configs = ' '.join([shlex.quote(f'{conf}.json') for conf in params['parameterSets']])
    configDepends = pathlib.Path(__file__).relative_to(output.absolute(), walk_up=True)
    args = ' '.join([shlex.quote(a) for a in sys.argv])

    log(DEBUG, stls)
    with open(output.joinpath("Makefile"), "w") as out:
      out.write(MAKEFILE_TMPL.format(includedMakefile=includedMakefile, stls=stls, configs=configs, configDepends=configDepends, configure=args))


if __name__ == '__main__':
  app.run(main)