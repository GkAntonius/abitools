from __future__ import print_function

import os
from os.path import join as pjoin
import warnings

import numpy as np

from ..utils import listify
from ..core import MPITask, IOTask
from ..io import AbinitInput

__all__ = ['AbinitTask']


class AbinitTask(MPITask, IOTask):
    """Base class for Abinit calculations."""

    _pseudo_dir = './'
    _pseudos = list()

    _TASK_NAME = 'Abinit'
    _TAG_JOB_COMPLETED = 'Calculation completed'

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
        pseudo_dir : str
            Path to the directory containing pseudopotential files.
        pseudos : list, str
            List of pseudopotential files.
        structure : pymatgen.Structure
            Structure object containing information on the unit cell.
        input_variables : dict
            A dictionary of input variables for initialization.
        bindir: str
            Path to the directory containing the abinit binaries.

        """

        super(AbinitTask, self).__init__(dirname, **kwargs)

        self._TASK_NAME = dirname

        self.rootname = rootname

        self.input = AbinitInput(fname=self.input_basename)

        self.pseudo_dir = kwargs.get('pseudo_dir', self.dirname)
        self.pseudos    = kwargs.get('pseudos', [])

        if 'structure' in kwargs:
            self.set_structure(kwargs['structure'])

        if 'input_variables' in kwargs:
            self.set_variables(kwargs['input_variables'])

        self.set_bindir(kwargs.get('bindir', ''))

        self.runscript.append('$MPIRUN $ABINIT < {} &> {} 2> {}'.format(
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
    def input_data_dir(self):
        return pjoin(self.dirname, 'input_data')

    @property
    def out_data_dir(self):
        return pjoin(self.dirname, 'out_data')

    @property
    def tmp_data_dir(self):
        return pjoin(self.dirname, 'tmp_data')

    @property
    def output_fname(self):
        return pjoin(self.dirname, self.output_basename)

    @property
    def input_fname(self):
        return pjoin(self.dirname, self.input_basename)

    @property
    def idat_root(self):
        """The root name for input data files."""
        return pjoin(self.input_data_dir, 'idat')

    @property
    def odat_root(self):
        """The root name for output data files."""
        return pjoin(self.out_data_dir, 'odat')

    @property
    def tmp_root(self):
        """The root name for temporaty data files."""
        return pjoin(self.tmp_data_dir, 'tmp')

    @property
    def pseudo_dir(self):
        return self._pseudo_dir

    @pseudo_dir.setter
    def pseudo_dir(self, value):
        if os.path.realpath(value) == value.rstrip(os.path.sep):
            self._pseudo_dir = value
        else:
            self._pseudo_dir = os.path.relpath(value, self.dirname)

    def set_pseudodir(self, value):
        self.pseudo_dir = value

    @property
    def pseudos(self):
        return self._pseudos

    @pseudos.setter
    def pseudos(self, value):
        self._pseudos = listify(value)

    def set_pseudos(self, value):
        self.pseudos = value

    def get_odat(self, datatype, dtset=0):
        """
        Returns an output data file name.

        Arguments
        ---------
        datatype:
            The type of datafile, e.g. 'DEN' or 'WFK'.

        dtset:
            The dataset index from which to take the data file.
            If 0 (the default), no dataset index is used.
        """
        fname = self.odat_root

        if int(dtset) > 0:
            fname += '_DS' + str(dtset)

        fname += '_' + datatype.lstrip('_')

        return fname

    def get_idat(self, datatype, dtset=0):
        """
        Returns an input data file name.

        Arguments
        ---------
        datatype:
            The type of datafile, e.g. 'DEN' or 'WFK'.

        dtset:
            The dataset index from which to take the data file.
            If 0 (the default), no dataset index is used.
        """
        fname = self.idat_root

        if int(dtset) > 0:
            fname += '_DS' + str(dtset)

        fname += '_' + datatype.lstrip('_')

        return fname

    def link_idat(self, fname, datatype, dtset=0):
        """
        Link a file as an input data.

        Arguments
        ---------

        fname: Name of the file to be linked.
        datatype: Suffix of the data file, e.g. 'DEN'
        dtset: Dataset specification. 0 means no dataset.

        """
        dest = os.path.relpath(self.get_idat(datatype, dtset), self.dirname)
        self.update_link(fname, dest)

    def link_io(self, idtset, odtset, datatype):
        """
        Link an output data file as an input data file.

        Arguments
        ---------

        idtset: Dataset that will read the file.
        odtset: Dataset that will output the file.
        datatype: Suffix of the data file, e.g. 'DEN'

        """
        target = self.get_odat(datatype, odtset)
        dest = os.path.relpath(self.get_idat(datatype, idtset), self.dirname)
        self.update_link(target, dest)

    def get_filesfile_content(self):
        S = ''
        S += self.input_basename + '\n'
        S += self.output_basename + '\n'
        for path in (self.idat_root, self.odat_root, self.tmp_root):
            S += os.path.relpath(path, self.dirname) + '\n'

        for pseudo in self.pseudos:
            pseudo_path = pjoin(self.pseudo_dir, pseudo)
            S += pseudo_path + '\n'  # pseudo_dir is already a relpath

        return S

    def write(self):

        # Main directory, etc...
        super(AbinitTask, self).write()

        self.check_pseudos()

        # Sub-directories
        for d in (self.input_data_dir, self.out_data_dir, self.tmp_data_dir):
            if not os.path.exists(d):
                os.mkdir(d)

        with self.exec_from_dirname():
            with open(self.filesfile_basename, 'w') as f:
                f.write(self.get_filesfile_content())

            self.input.write()

    def check_pseudos(self):
        """Check that pseudopotential files exist."""
        for pseudo in self.pseudos:
            fname = os.path.relpath(
                    os.path.join(self.dirname, self.pseudo_dir, pseudo))
            if not os.path.exists(fname):
                warnings.warn('Pseudopotential not found:\n{}'.format(fname))

    def set_comment(self, *args, **kwargs):
        """Set a comment in the input file."""
        __doc__ = self.input.set_comment.__doc__
        self.input.set_comment(*args, **kwargs)

    def set_structure(self, *args, **kwargs):
        """Set the structure using a pymatgen.Structure object."""
        self.input.set_structure(*args, **kwargs)

    def set_variables(self, *args, **kwargs):
        """Set input variables."""
        self.input.set_variables(*args, **kwargs)

    def set_bindir(self, path):
        self.runscript['ABINIT'] = os.path.join(path, 'abinit')

    @property
    def ndtset(self):
        return self.input.ndtset

    @ndtset.setter
    def ndtset(self, value):
        self.input.ndtset = value

    @property
    def jdtset(self):
        return self.input.jdtset

    @jdtset.setter
    def jdtset(self, value):
        self.input.jdtset = value
