## Usage

Default workflow:

* Create a new directory, preferably outside this repo, to hold the generated stl files, and `cd` into that directory.
* run `${PATH_TO_REPO}/bin/configure.py` with the right options. This creates a directory tree containing the `.json` configs and a`Makefile` in each directory.
* run `make` , use a small `-j` , but openscad does some parallelization on it's own. 


### configure.py options

* `--config` this is one or multiple of the configs in the `configs` directory. At least one must be given.
* if config contains at least one remix config, 
  then `--remix_input` must be provided. 
  This takes a 
  [glob](https://docs.python.org/3/library/pathlib.html#pathlib-pattern-language) as input, 
  

Shield: [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg