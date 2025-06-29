import pathlib

from absl import flags


BASEDIR = pathlib.Path(__file__).resolve().parents[2].relative_to(pathlib.Path('.').resolve(), walk_up=True)
U = 12.7  # one unit = 0.5in

flags.DEFINE_string('scadpath', str(BASEDIR.joinpath('scad')), 'Path to the scad files')
FLAGS = flags.FLAGS

_SCADPATH = None
def scadpath() -> pathlib.Path:
  global _SCADPATH
  if not _SCADPATH:
    _SCADPATH = pathlib.Path(FLAGS.scadpath).resolve()
  return _SCADPATH