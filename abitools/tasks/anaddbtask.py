from __future__ import print_function

import os
from os.path import join as pjoin
import warnings

import numpy as np

from ..utils import listify
from ..core import MPITask, IOTask
from ..io import AnaddbInput

__all__ = ['AnaddbTask']


class AnaddbTask(MPITask, IOTask):
    """Base class for Anaddb calculations."""

    _TASK_NAME = 'Anaddb'
    _TAG_JOB_COMPLETED = 'the run completed succesfully'

    def __init__(self, dirname, rootname='calc', **kwargs):
        """
        Arguments
        ---------

        dirname : str
            Directory in which the files are written and the code is executed.
            Will be created if needed.

        Keyword arguments
        -----------------

        rootname : str
            Prefix used as a rootname for abinit calculations.
        ddb_fname : str
            Name of the ddb file.
        gkk_fname : str
            Name of the gkk file.
        ddk_fname : str
            Name of the ddk file.
        input_variables : dict
            A dictionary of input variables for initialization.
        bindir: str
            Path to the directory containing the abinit binaries.

        """

        super(AnaddbTask, self).__init__(dirname, **kwargs)

        self._TASK_NAME = dirname

        self.rootname = rootname

        self.ddb_basename = 'ddb'
        self.band_eps_basename = 'band_eps'
        self.gkk_basename = 'gkk'
        self.anaddb_ep_basename = 'anaddb.ep'
        self.ddk_basename = 'ddk'

        if 'ddb_fname' in kwargs:
            self.ddb_fname = kwargs['ddb_fname']
        if 'gkk_fname' in kwargs:
            self.gkk_fname = kwargs['gkk_fname']
        if 'ddk_fname' in kwargs:
            self.ddk_fname = kwargs['ddk_fname']

        self.input = AnaddbInput(fname=self.input_basename)

        if 'input_variables' in kwargs:
            self.set_variables(kwargs['input_variables'])

        self.set_bindir(kwargs.get('bindir', ''))

        self.runscript.append('$MPIRUN $ANADDB < {} &> {} 2> {}'.format(
            self.filesfile_basename, self.log_basename, self.stderr_basename))

    @property
    def filesfile_basename(self):
        return self.rootname + '.files'

    @property
    def input_basename(self):
        return self.rootname + '.in'

    @property
    def output_basename(self):
        return self.rootname + '.out'

    @property
    def log_basename(self):
        return self.rootname + '.log'

    @property
    def stderr_basename(self):
        return 'stderr'

    @property
    def output_fname(self):
        return pjoin(self.dirname, self.output_basename)

    @property
    def input_fname(self):
        return pjoin(self.dirname, self.input_basename)

    @property
    def ddb_fname(self):
        return pjoin(self.dirname, self.ddb_basename)

    @ddb_fname.setter
    def ddb_fname(self, fname):
        dest = self.ddb_basename
        self.update_link(fname, dest)

    @property
    def gkk_fname(self):
        return pjoin(self.dirname, self.gkk_basename)

    @gkk_fname.setter
    def gkk_fname(self, fname):
        dest = self.gkk_basename
        self.update_link(fname, dest)

    @property
    def ddk_fname(self):
        return pjoin(self.dirname, self.ddk_basename)

    @ddk_fname.setter
    def ddk_fname(self, fname):
        dest = self.ddk_basename
        self.update_link(fname, dest)

    def get_odat(self, datatype):
        """
        Returns an output data file name.

        Arguments
        ---------
        datatype:
            The type of datafile, e.g. 'DDB' or 'PHBS.nc'.

        """
        fname = self.output_fname

        fname += '_' + datatype.lstrip('_')

        return fname

    def get_filesfile_content(self):
        files = [self.input_basename, self.output_basename,
                 self.ddb_basename, self.band_eps_basename,
                 self.gkk_basename, self.anaddb_ep_basename,
                 self.ddk_basename]

        S = '\n'.join(files) + '\n'
        return S

    def write(self):

        # Main directory, etc...
        super(AnaddbTask, self).write()

        with self.exec_from_dirname():
            with open(self.filesfile_basename, 'w') as f:
                f.write(self.get_filesfile_content())

            self.input.write()

    def set_comment(self, *args, **kwargs):
        """Set a comment in the input file."""
        __doc__ = self.input.set_comment.__doc__
        self.input.set_comment(*args, **kwargs)

    def set_variables(self, *args, **kwargs):
        """Set input variables."""
        self.input.set_variables(*args, **kwargs)

    def set_bindir(self, path):
        self.runscript['ANADDB'] = os.path.join(path, 'anaddb')

