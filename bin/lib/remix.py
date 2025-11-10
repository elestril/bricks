"""
Remix module for converting existing STL files into brick configurations.

This module handles the "remix" workflow where existing 3D models (STL files)
are analyzed and converted into parameterized brick configurations based on
regex pattern matching and YAML configuration rules.
"""

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

# Command-line flags for remix operations
flags.DEFINE_string('input', None, 'Base input directory.')
flags.DEFINE_multi_string('remix', [], '<remixconfig>:<fileglob> config and input stls to remix')
FLAGS = flags.FLAGS

class Remix:
  """Processes existing STL files and converts them to brick configurations.

  The Remix class reads STL files from an input directory, matches them against
  regex patterns, and generates brick configurations based on YAML rules."""

  def __init__(self, name, config):
    """Initialize a Remix configuration.

    Args:
      name: Name of this remix configuration
      config: Dictionary containing 'regex' patterns and 'config' rules

    Raises:
      ValueError: If --input flag is not set or if this remix is not enabled
    """
    if not FLAGS.input:
      raise ValueError(f'--input is not defined, nothing to remix')
    if FLAGS.remix and name not in self._remixes:
      raise ValueError(f'{name} not enabled in --remix: {FLAGS.remix}')

    # Determine which files to process based on the remix configuration
    self._glob = self._remixes.get(name) or pathlib.Path(FLAGS.input).glob('**/*.stl')
    # Compile regex patterns for matching filenames
    self._regex = [re.compile(r) for r in config['regex']]
    self.name = name
    self.config = config['config']

  @functools.cached_property
  def _remixes(self) -> Dict[str, Iterator[pathlib.Path]]:
    """Parse --remix flags into a dict mapping config names to file globs.

    Returns:
      Dict mapping remix config names to file path iterators
    """
    return {
        conf: pathlib.Path(FLAGS.input).glob(glob) for (conf, glob) in [r.split(':', 1) for r in FLAGS.remix]
    }

  @functools.cached_property
  def _input(self) -> pathlib.Path:
    """Get the resolved input directory path.

    Returns:
      Absolute path to the input directory
    """
    return pathlib.Path(FLAGS.input).resolve()

  @functools.cached_property
  def bricks(self) -> Iterator[Brick]:
    """Generate Brick objects from matching STL files.

    Yields:
      Brick: Successfully configured brick objects
    """
    for infile in self._glob:
      logging.debug("remixing %s", infile)
      try:
        yield self._remix(infile)
      except InvalidBrick as e:
        logging.info('%s: cannot remix with config %s: %s ', infile.name, self.name, e)
        STATS[self.name]['invalid'] += 1


  def _remix(self, infile: pathlib.Path) -> Optional[Brick]:
    """Process a single STL file and generate a Brick configuration.

    Matches the filename against regex patterns, extracts mesh dimensions,
    and applies configuration rules to create a Brick object.

    Args:
      infile: Path to the STL file to process

    Returns:
      Configured Brick object

    Raises:
      InvalidBrick: If filename doesn't match any regex or configuration is invalid
    """

    # Try to match filename against all regex patterns
    for match in [r.fullmatch(infile.name) for r in self._regex]:
      if match:
        logging.debug('%s: regex match %r', self.name, match.capturesdict())
        break
    else:
      raise InvalidBrick(f'{infile.name} does not match any regex')

    # Load STL mesh and extract dimensions
    mesh = stl.Mesh.from_file(infile)
    vars = {
      'meshMin': mesh.min_.tolist(),
      'meshMax': mesh.max_.tolist(),
      'meshDimension': [round(c) / 4 for c in ((mesh.max_ - mesh.min_) * 4.0 / U ).tolist()],
    }
    # Add regex capture groups as variables
    vars.update(((f'{k}', ''.join(v)) for (k,v) in match.capturesdict().items()))
    # Add path components as variables (last 5 parts in reverse)
    vars.update(((f'path{i}',v) for (i,v) in enumerate(infile.parts[:-5:-1])))

    # Build initial brick configuration from mesh data
    brickConfig = {
      'name': infile.stem,
      'set': self.name,
      'input': infile.resolve(),
      'inputMin': copy.copy(vars['meshMin']),
      'inputMax': copy.copy(vars['meshMax']),
      'path': pathlib.Path(self.name, infile.parent.name.replace(' ', '')),
      'size': copy.copy(vars['meshDimension'])
    }

    # Apply configuration rules from YAML based on matched groups
    for (group) in self.config:
      subconf = self.config[group]
      # Universal config (applies to all)
      if group == '*':
        brickConfig.update(subconf)
        continue

      # Build the subkey from matched groups
      matchgroups = group.split('/')
      subkey = '/'.join([vars[g] for g in matchgroups])

      # Apply wildcard config for this group
      scval = subconf.get('*', {})
      if scval == False:
        raise InvalidBrick(f'{infile}: Config for {group}:{subkey} set to "False"')
      brickConfig.update(scval)

      # Apply specific config for this subkey (or default '_')
      scval = subconf.get(subkey, subconf.get('_', {}))
      if scval == False:
        raise InvalidBrick(f'{infile}: Config for {group}:{subkey} set to "False"')
      brickConfig.update(scval)

    # Expand template variables in string values
    vars['config'] = brickConfig
    logging.debug('Available variables for config expansion: %s', ', '.join([f'{var}="{val}"' for (var,val) in vars.items()]))
    for (k,v) in brickConfig.items():
      if type(v) is str:
        brickConfig[k] = v.format(**vars)

    # Create and return the Brick object
    logging.debug('Brick config: %r', brickConfig)
    brick = Brick(**brickConfig)
    logging.debug('Success: %s', brick)
    return brick


