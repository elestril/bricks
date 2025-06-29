from __future__ import annotations

import copy
import functools
import itertools

from typing import Dict, Iterator, Optional, Sequence
from absl import flags, logging

from lib.brick import Brick, InvalidBrick


flags.DEFINE_multi_string('generate', [], '<generateconfig> bricks to generate.')
FLAGS = flags.FLAGS

class Generate:
  def __init__(self, name: str, config: Dict):
    if FLAGS.generate and name not in FLAGS.generate:
      raise ValueError(f'{name} not enabled in --generate: {FLAGS.generate}')
    self.name = name
    self.generate = config['generate']
    self.condition = config.get('condition', 'True')
    self.config = config.get('config',{})

  @functools.cached_property
  def bricks(self) -> Iterator[Brick]:
    for itervals in itertools.product(*self.generate.values()):
      conf = copy.deepcopy(self.config)
      conf.update({k:v for (k,v) in zip(self.generate.keys(), itervals)})
      if not eval(self.condition.format_map(conf)):
        continue
      yield Brick(**conf)