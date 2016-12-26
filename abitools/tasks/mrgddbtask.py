from __future__ import print_function

import os
from os.path import relpath
import warnings

from ..core import Writable
from .abinittask import AbinitTask

__all__ = ['MrgddbTask', 'MrgddbInput']


class MrgddbTask(AbinitTask):
    """Task to merge DDB files with mrgddb."""

    _nproc = 1
    _TASK_NAME = 'Mrgddb'
    _TAG_JOB_COMPLETED = 'the run completed successfully'

    def __init__(self, dirname, ddb_fnames, rootname='mrgddb', **kwargs):
        """
        Arguments
        ---------

        dirname : str
            Directory in which the files are written and the code is executed.
            Will be created if needed.

        ddb_fnames: list
            List of DDB files to be merged.

        Keyword arguments
        -----------------

        rootname : str
            Prefix used as a rootname for abinit calculations.
        bindir: str
            Path to the directory containing the abinit binaries.

        Properties
        ----------

        ddb_fname: str
            The path to the merged DDB file produce.

        """

        super(AbinitTask, self).__init__(dirname, **kwargs)

        self._TASK_NAME = dirname

        self.rootname = rootname

        self.input = MrgddbInput(
            fname=self.input_basename,
            out_fname=relpath(self.ddb_fname, self.dirname),
            ddb_fnames=[relpath(f, self.dirname) for f in ddb_fnames],
            )

        self.set_bindir(kwargs.get('bindir', ''))

        self.runscript.append('$MPIRUN $MRGDDB < {} &> {} 2> {}'.format(
            self.input_basename, self.output_basename, self.stderr_basename))

        self.nproc = 1

    def write(self):

        # Main directory, etc...
        super(AbinitTask, self).write()

        # Sub-directories
        for d in (self.out_data_dir,):
            if not os.path.exists(d):
                os.mkdir(d)

        with self.exec_from_dirname():
            self.input.write()

    def set_bindir(self, path):
        self.runscript['MRGDDB'] = os.path.join(path, 'mrgddb')

    @property
    def ddb_fname(self):
        return self.get_odat('DDB')

    merged_ddb_fname = ddb_fname


class MrgddbInput(Writable):

    def __init__(self, fname, out_fname, ddb_fnames, **kwargs):

        super(MrgddbInput, self).__init__(fname=fname, **kwargs)

        self.out_fname = out_fname
        self.ddb_fnames = ddb_fnames

    def __str__(self):
        nfiles = len(self.ddb_fnames)
        lines = [self.out_fname, '#', str(nfiles)]
        lines.extend(self.ddb_fnames)
        return '\n'.join(lines) + '\n'
        
    @property
    def nproc(self):
        return self._nproc

    @nproc.setter
    def nproc(self, value):
        if value != 1:
            warnings.warn('nproc can only be 1.')
        self._nproc = 1
        self._declare_mpirun()

    def set_variables(self, *args, **kwargs):
        pass

    def set_structure(self, *args, **kwargs):
        pass

