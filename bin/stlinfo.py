#!/usr/bin/python3

import sys
import stl
import numpy as np
from string import Template
from absl import app, flags, logging
import json

FLAGS = flags.FLAGS
flags.DEFINE_string('stl', None, 'input stl file')
flags.mark_flag_as_required('stl')
flags.DEFINE_string('json_output', None, 'write a json output file')


U = 12.7  # grid unit is 1/2in 

def main(argv):
  del argv

  msh = stl.mesh.Mesh.from_file(FLAGS.stl)

  params = {}
  params['input'] = FLAGS.stl
  params['minv'] = (np.round(msh.min_ * 2 / U )/ 2).tolist()
  params['maxv'] = (np.round(msh.max_ * 2 / U )/ 2).tolist()

  logging.log(logging.INFO, params)

  if FLAGS.json_output:
    with open(FLAGS.json_output, "w") as out:
      out.write(json.dumps(
        {
          'parameterSets': { 
            'default': params
          }
        }, 
        sort_keys=True,
        indent=2
      )) 

if __name__ == '__main__':
  app.run(main)