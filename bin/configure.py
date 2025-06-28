#!/usr/bin/python3


import collections
import datetime
import copy
import itertools
import json
import numpy as np
import mergedeep
import regex as re
import logging as pylogging
import shlex
import io

import sys
import pathlib

from absl import app, flags, logging
from ruamel.yaml import YAML
from string import Template

from lib.globals import BASEDIR
from lib.stats import STATS
from lib.bricks import Bricks

yaml = YAML()


FLAGS = flags.FLAGS
flags.DEFINE_string('configs', str(BASEDIR.joinpath('configs', '*.yaml')), 'Path to the yaml configs')
flags.DEFINE_string('logfile', 'configure.log', 'Location of the logfile')


#### Code ####

def main(argv): 

  logging.get_absl_handler().setFormatter(pylogging.Formatter('%(message)s'))

  config = Bricks()
  ymls = pathlib.Path('.').glob(FLAGS.configs)

  config.configure(ymls)
  config.writeJsonConfigs()

  with io.StringIO() as ybuf:
    yaml.dump({str(k): dict(v) for (k,v) in STATS.items()}, ybuf)
    print(f'\n\n**** STATS ****\n\n{ybuf.getvalue()}')

  return
if __name__ == '__main__':
  app.run(main)