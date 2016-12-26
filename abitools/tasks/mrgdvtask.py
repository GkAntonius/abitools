from __future__ import print_function

import os
from os.path import relpath
import warnings

from ..core import Writable
from .abinittask import AbinitTask

__all__ = ['MrgdvTask', 'MrgdvInput']


class MrgdvTask(AbinitTask):
    """Task to merge POT files with mrgdv."""

    _nproc = 1
    _TASK_NAME = 'Mrgdv'
    _TAG_JOB_COMPLETED = 'Done'

    def __init__(self, dirname, pot_fnames, rootname='mrgdv', **kwargs):
        """
        Arguments
        ---------

        dirname : str
            Directory in which the files are written and the code is executed.
            Will be created if needed.

        pot_fnames: list
            List of POT files to be merged.

        Keyword arguments
        -----------------

        rootname : str
            Prefix used as a rootname for abinit calculations.
        bindir: str
            Path to the directory containing the abinit binaries.

        Properties
        ----------

        dvdb_fname: str
            The path to the merged DDB file produce.

        """

        super(AbinitTask, self).__init__(dirname, **kwargs)

        self._TASK_NAME = dirname

        self.rootname = rootname

        self.input = MrgdvInput(
            fname=self.input_basename,
            out_fname=relpath(self.dvdb_fname, self.dirname),
            pot_fnames=[relpath(f, self.dirname) for f in pot_fnames],
            )

        self.set_bindir(kwargs.get('bindir', ''))

        self.runscript.append('$MPIRUN $MRGDV < {} &> {} 2> {}'.format(
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
        self.runscript['MRGDV'] = os.path.join(path, 'mrgdv')

    @property
    def dvdb_fname(self):
        return self.get_odat('DVDB')


class MrgdvInput(Writable):

    def __init__(self, fname, out_fname, pot_fnames, **kwargs):

        super(MrgdvInput, self).__init__(fname=fname, **kwargs)

        self.out_fname = out_fname
        self.pot_fnames = pot_fnames

    def __str__(self):
        nfiles = len(self.pot_fnames)
        lines = [self.out_fname, str(nfiles)]
        lines.extend(self.pot_fnames)
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

