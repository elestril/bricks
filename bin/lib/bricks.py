"""
Bricks module for managing brick configurations and generating OpenSCAD files.

This module provides the main Bricks class that orchestrates the brick configuration
system, including loading YAML configs, managing brick sets (Generate and Remix),
and writing OpenSCAD output files.
"""

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

# Command-line flags
flags.DEFINE_string('output', '.', 'Output directory (root of output hierarchy).')
flags.register_validator('output', lambda o: pathlib.Path(o).is_dir(), message='output must be an existing directory.')

flags.DEFINE_bool('force', False, 'Overwrite unchanged files.')
FLAGS = flags.FLAGS

yaml = YAML()

# Grid unit is 1/2 inch = 12.7mm
U = 12.7

# Template for generating Makefiles in output directories
MAKEFILE_TMPL = """
include {incl}

"""


class Bricks:
  """Main orchestrator for brick configuration and OpenSCAD file generation.

  This class manages all brick sets (both generated and remixed), processes
  YAML configuration files, and writes OpenSCAD files with JSON parameter sets.

  Attributes:
    bricksets: Dictionary of BrickSet objects (Generate or Remix instances)
    _bricks: Internal dictionary of Brick objects by name
    outpaths: Set of output paths that have been written
    generates: Dictionary tracking which generate configs are enabled
  """

  def __init__(self):
    """Initialize the Bricks configuration system."""
    self.bricksets: Dict[str, BrickSet] = dict()
    self._bricks: Dict[str, Brick] = dict()

    self.outpaths = set()
    logging.debug('remix: %r', FLAGS.remix)
    self.generates = {
      conf:True for conf in FLAGS.generate
    }


  def configure(self, ymls: Sequence[pathlib.Path]):
    """Load and process YAML configuration files.

    Reads YAML files and creates Generate and Remix brick sets based on
    the configurations found. Invalid configurations are logged and skipped.

    Args:
      ymls: Sequence of paths to YAML configuration files
    """ 
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
    """Add a brick set to the collection.

    Args:
      brickset: A BrickSet instance (Generate or Remix)

    Raises:
      KeyError: If a brick set with this name already exists
    """
    if brickset.name in self.bricksets:
      raise KeyError('Duplicate brickset "{brickset.name}"')
    self.bricksets[brickset.name] = brickset


  def bricks(self) -> Iterator[Brick]:
    """Iterate over all bricks from all brick sets.

    Yields:
      Brick: Each brick from each brick set
    """
    for brickset in self.bricksets.values():
      yield from brickset.bricks


  def writeConfigs(self):
    """Generate and write OpenSCAD files and JSON parameter sets.

    This method:
    1. Reads the OpenSCAD template
    2. Creates a Makefile if needed
    3. Generates OpenSCAD files for each brick
    4. Tracks statistics (new, updated, unchanged files)
    5. Writes a config.json with all parameter sets
    """
    global STATS

    # Load the OpenSCAD template file
    with open(scadpath().joinpath('brick.template.scad')) as tmpl:
      scadTemplate = tmpl.read()

    output = pathlib.Path(FLAGS.output)

    # Create Makefile in output directory if it doesn't exist
    if not output.joinpath('Makefile').exists():
      with open(output.joinpath('Makefile'), 'w') as fd:
        fd.write(MAKEFILE_TMPL.format(incl=BASEDIR.joinpath('Makefile.mk').resolve().relative_to(output.resolve(), walk_up=True)))

    # Load existing config.json to track changes
    jsonConfigPath = pathlib.Path(output).joinpath('config.json')
    jsonConfig = {}
    if jsonConfigPath.exists():
      with open(jsonConfigPath, 'r') as jfd:
        jsonConfig = json.load(jfd).get('parameterSets', {})

    # Process each brick
    for brick in self.bricks():

      scadConfigItems = brick.scadConfigItems()
      scadFile = output.joinpath(brick.path, brick.name + '.scad').resolve()

      logging.debug('writing %s/%s: %r', brick.path, brick.name, scadConfigItems)

      # Skip unchanged files unless --force is specified
      if not FLAGS.force and brick.scadConfigItems() == jsonConfig.get(brick.name, {}) and scadFile.exists():
        STATS[brick.set]['unchanged'] += 1
        STATS['total']['unchanged'] += 1
        logging.info(f'{brick.name}: Unchanged')
        continue

      # Update JSON config and format template
      jsonConfig[brick.name] = scadConfigItems
      scadConfig = scadTemplate.format_map(scadConfigItems)

      # Create output directory if needed
      if not scadFile.parent.exists():
        scadFile.parent.mkdir(parents=True)

      # Track whether this is a new or updated file
      if scadFile.exists():
        neworupdate = 'updated'
      else:
        neworupdate = 'new'

      # Write the OpenSCAD file
      with open(scadFile, 'w') as fd:
        fd.write(scadConfig)
        logging.info(f'{brick.name}: {neworupdate}')
        STATS[brick.set][neworupdate] += 1
        STATS['total'][neworupdate] += 1

    # Write the master config.json with all parameter sets
    with open(jsonConfigPath, 'w') as fd:
      json.dump(
        {'parameterSets': jsonConfig,
        'fileFormatVersion': '1',
      }, fd, indent=2)

  def __str__(self):
    """String representation of the Bricks object.

    Returns:
      The name attribute (if it exists)
    """
    return self.name
