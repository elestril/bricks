"""
Generate module for programmatically creating brick configurations.

This module handles the "generate" workflow where bricks are created by
iterating over parameter combinations and applying conditional filters.
"""

from __future__ import annotations

import copy
import functools
import itertools

from typing import Dict, Iterator, Optional, Sequence
from absl import flags, logging

from lib.brick import Brick, InvalidBrick

# Command-line flag for selecting which generate configs to use
flags.DEFINE_multi_string('generate', [], '<generateconfig> bricks to generate.')
FLAGS = flags.FLAGS

class Generate:
  """Generates bricks by iterating over parameter combinations.

  The Generate class creates bricks by computing the Cartesian product of
  parameter ranges and filtering them with optional conditions."""

  def __init__(self, name: str, config: Dict):
    """Initialize a Generate configuration.

    Args:
      name: Name of this generate configuration
      config: Dictionary containing 'generate', 'condition', and 'config' keys

    Raises:
      ValueError: If this generate config is not enabled via --generate flag
    """
    if FLAGS.generate and name not in FLAGS.generate:
      raise ValueError(f'{name} not enabled in --generate: {FLAGS.generate}')
    self.name = name
    self.generate = config['generate']  # Parameter ranges to iterate over
    self.condition = config.get('condition', 'True')  # Filter condition
    self.config = config.get('config',{})  # Base configuration

  @functools.cached_property
  def bricks(self) -> Iterator[Brick]:
    """Generate Brick objects from parameter combinations.

    Creates the Cartesian product of all parameter ranges, applies the
    condition filter, and yields Brick objects for valid combinations.

    Yields:
      Brick: Configured brick objects that pass the condition filter
    """
    # Iterate over all combinations of parameter values
    for itervals in itertools.product(*self.generate.values()):
      conf = copy.deepcopy(self.config)
      # Merge the current parameter values into the config
      conf.update({k:v for (k,v) in zip(self.generate.keys(), itervals)})
      # Apply the condition filter (if specified)
      if not eval(self.condition.format_map(conf)):
        continue
      yield Brick(**conf)