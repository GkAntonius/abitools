from __future__ import print_function
import sys
import os
import shutil

if sys.version[0:3] < '2.7':
    sys.stderr.write("Python version 2.7 or above is required. Exiting.")
    sys.exit(1)

try:
    import setuptools
except ImportError:
    sys.stderr.write(
    "Please install setuptools before running this script. Exiting.")
    sys.exit(1)

from setuptools import setup, find_packages


# --------------------------------------------------------------------------- #
# Basic project information
# --------------------------------------------------------------------------- #

name = 'abitools'
description = 'A simple python interface for Abinit calculations.'
author = 'Gabriel Antonius'
author_email = 'antonius@lbl.gov'
license = 'GPL'
__version__ = '4.0.1'


# Requirements
install_requires = [
    'numpy >=1.6',
    'pymatgen >=4.0',
    ]

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def install_user_configuration():
    user_config = os.path.join('config', 'user_configuration.py')
    dest = os.path.join('abitools', 'config', 'user_configuration.py')
    if os.path.exists(user_config):
        shutil.copy(user_config, dest)


# --------------------------------------------------------------------------- #
# Setup
# --------------------------------------------------------------------------- #

install_user_configuration()

setup_args = dict(
      name             = name,
      version          = __version__,
      description      = description,
      author           = author,
      author_email     = author_email,
      license          = license,
      install_requires = install_requires,
      packages         = find_packages(),
      #package_data     = get_package_data(),
      )

if __name__ == "__main__":
    setup(**setup_args)

