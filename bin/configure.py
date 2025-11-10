#!/usr/bin/python3
"""
Brick configuration builder script.

This script processes YAML configuration files to generate OpenSCAD files for 3D printable bricks.
It reads brick configurations, processes them through the Bricks class, and outputs statistics.
"""

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

# Command-line flags
FLAGS = flags.FLAGS
flags.DEFINE_string('configs', str(BASEDIR.joinpath('configs', '*.yaml')), 'Path to the yaml configs')
flags.DEFINE_string('logfile', 'configure.log', 'Location of the logfile')


#### Code ####

def main(argv):
  """Main entry point for the brick configuration script.

  Args:
    argv: Command-line arguments (unused but required by absl.app)
  """ 

  # Configure logging to show only the message (no timestamps, etc.)
  logging.get_absl_handler().setFormatter(pylogging.Formatter('%(message)s'))

  # Initialize the brick configuration system
  config = Bricks()
  ymls = pathlib.Path('.').glob(FLAGS.configs)

  # Process all YAML configuration files
  config.configure(ymls)
  # Write the generated OpenSCAD files
  config.writeConfigs()

  # Output statistics to console
  with io.StringIO() as ybuf:
    yaml.dump({str(k): dict(v) for (k,v) in STATS.items()}, ybuf)
    print(f'\n\n**** STATS ****\n\n{ybuf.getvalue()}')

  return

if __name__ == '__main__':
  app.run(main)