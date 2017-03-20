from __future__ import print_function, division
import textwrap
import numpy as np

from ..utils import listify, angstrom_to_bohr, header_line
from ..core.writable import Writable
from .sorting import input_variable_blocks
from .variable import InputVariable
from .structures import structure_to_abivars

__all__ = ['AbinitInput']


class AbinitInput(Writable):
    """
    Abinit input file.

    Example usage:

    >> kpoint_grid_shifted = {
    >>     'kptopt' : 1,
    >>     'ngkpt' : 3*[4],
    >>     'nshiftk' : 4,
    >>     'shiftk' : [[0.5,0.5,0.5],
    >>                 [0.5,0.0,0.0],
    >>                 [0.0,0.5,0.0],
    >>                 [0.0,0.0,0.5]],}
    >> 
    >> kpoint_grid_unshifted = {
    >>     'kptopt' : 1,
    >>     'ngkpt' : 3*[4],
    >>     'nshiftk' : 1,
    >>     'shiftk' : [0,0,0],}
    >> 
    >> cell = {
    >>     'ntypat' : 1
    >>     'znucl'  : 6.0
    >>     'natom'  : 2
    >>     'typat'  : [1, 1]
    >>     'xred'   : [[0,0,0],[0.25,0.25,0.25]]
    >>     'acell'  : 3*[6.9]
    >>     'rprim'  : [[0.0,0.5,0.5],
    >>                 [0.5,0.0,0.5],
    >>                 [0.5,0.5,0.0]]}
    >> 
    >> f = InputFile()
    >> 
    >> f.ndtset = 3
    >> f.set_variables({'ecut' : 4.0, 'ecutsm' : 0.5})
    >> f.set_variables(cell)
    >> 
    >> f.set_variables(kpoint_grid_shifted, dataset=1)
    >> f.set_variables(kpoint_grid_unshifted, dataset=[2, 3])
    >> 
    >> f.write('myfile.in')
    """

    _ndtset = 0
    _jdtset = None
    _udtset = None

    def __init__(self, comment='', **kwargs):

        super(AbinitInput, self).__init__(**kwargs)

        self.variables = dict()
        self.decimals = dict()
        self.comment = comment
        self.dataset_comments = dict()

    def set_comment(self, comment, dataset=None):
        """Write a comment for the input or for one dataset."""
        if not dataset:
            self.comment = comment
        else:
            self.dataset_comments[dataset] = comment

    def __str__(self):

        # Initialize variable blocks
        ds = VariableBlock('', comment=self.comment, sort=False)
        common = SortedVariableBlock('Common variables')
        special = VariableBlock('Automatic variables')
    
        datasets = list()
        if self.jdtset:
            for j in self.jdtset:
                block = VariableBlock('Dataset {}'.format(j))
                block.comment = self.dataset_comments.get(j, '')
                datasets.append(block)


        # Make the first block
        for varname in ('ndtset', 'jdtset', 'udtset'):
            value = getattr(self, varname)
            if value:
                ds.append(InputVariable(varname, value))

        # Sort variables
        jdtset = list(self.jdtset) if self.jdtset else list()
        for name, value in self.variables.items():
            variable = InputVariable(name, value,
                                     decimals=self.decimals.get(name, 0))

            j = variable.dataset

            if not j:
                common.append(variable)

            elif j.isdigit():
                j = int(j)

                if j not in jdtset:
                    # Create a new block if needed
                    block = VariableBlock('Dataset {}'.format(j))
                    block.comment = self.dataset_comments.get(j, '')
                    i = np.searchsorted(jdtset, j)
                    jdtset.insert(i, j)
                    datasets.insert(i, block)

                else:
                    i = jdtset.index(j)

                datasets[i].append(variable)

            else:
                special.append(variable)

        # Title is not needed if there is only one block
        if not special and not datasets:
            common.title = ''

        # Format the input file
        blocks = [ds, special] + datasets + [common]
        S = ''
        for block in blocks:
            if block:
                S += str(block) + '\n'

        return S


    def clear(self):
        """Clear variables."""
        self.variables.clear()

    def set_variable(self, name, value, decimals=None):  # TODO ndecimal or ndigits 
        """Set a single variable."""

        if name in ('ndtset', 'jdtset', 'udtset'):
            setattr(self, name, value)

        self.variables[name] = value
        if value is None:
            del self.variables[name]
            return
        if decimals is not None:
            self.decimals[name] = decimals

    def set_variables(self, variables, dataset=0, **kwargs):
        """
        Sets variables by providing a dictionary, or expanding a dictionary,
        and possibly append them by a dataset index.
        """
        #variables.update(kwargs)

        if not dataset:
            dataset = ['']

        for ds in listify(dataset):
            for (key, val) in variables.items():
                newkey = key + str(ds)
                self.set_variable(newkey, val, **kwargs)

    def set_structure(self, structure):
        """Use a pymatgen.Structure object to define the unit cell."""
        variables = structure_to_abivars(structure)
        self.set_variables(variables)

    @property
    def ndtset(self):
        return self._ndtset

    @ndtset.setter
    def ndtset(self, value):
        self._ndtset = int(value)

        if self._ndtset > 1 and not self.jdtset and not self.udtset:
            self.jdtset = range(1, self._ndtset+1)

    @property
    def jdtset(self):
        return self._jdtset

    @jdtset.setter
    def jdtset(self, value):
        self._jdtset = map(int, listify(value))
        self.ndtset = len(self._jdtset)

        if self.udtset:
            self._udtset = None

    @property
    def udtset(self):
        return self._udtset

    @udtset.setter
    def udtset(self, value):
        self._udtset = map(int, listify(value))
        self.ndtset = np.prod(self._udtset)

        if self.jdtset:
            self._jdtset = None


# =========================================================================== #


class VariableBlock(list):
    """A block of abinit variables."""

    def __init__(self, title, comment='', header_size=80, sort=True): 

        self.title = title
        self.comment = comment
        self.header_size = header_size
        self.sort = sort

    def clear(self):
        del self[:]

    @property
    def header(self):
        if not self.title and not self.comment:
            return ''

        title = header_line(self.title, self.header_size)

        comment = ''
        comment_lines = textwrap.wrap(self.comment, width=self.header_size)
        for line in comment_lines:
            if not line.startswith('# '):
                line = '# ' + line
            comment += line + '\n'

        if not self.comment:
            header = title
        elif not self.title:
            header = comment
        else:
            header = title + '\n' + comment

        return header

    def __str__(self):

        if not self:
            return ''

        lines = list()
        if self.header:
            lines.append(self.header)

        # Choose the iterator
        if self.sort:
            variables = sorted(self)
        else:
            variables = iter(self)

        for variable in variables:
            svar = str(variable)
            if svar:
                lines.append(svar)
        return '\n'.join(lines) + '\n'


class SortedVariableBlock(VariableBlock):
    """A variable block that gets sorted into subblocks."""

    def get_section_blocks(self):
        """
        Sort variables into sections and return new variable blocks
        for each section.
        """
        blocks = list()

        for (name, register) in input_variable_blocks.items():

            register = register.split()

            block = VariableBlock(name, header_size=self.header_size//2)

            for i in reversed(range(len(self))):
                variable = self[i]
                if variable.basename in register:
                    block.append(self.pop(i))

            if block:
                blocks.append(block)

        if self:
            block = VariableBlock('Unsorted', header_size=self.header_size//2)
            block.extend(self)
            blocks.append(block)

            self.clear()

        return blocks

    def __str__(self):

        if not self:
            return ''

        S = ''
        if self.header:
            S += self.header + '\n'

        blocks = self.get_section_blocks()
        for block in blocks:
            S += '\n' + str(block)

        return S

