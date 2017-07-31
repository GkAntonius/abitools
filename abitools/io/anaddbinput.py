from __future__ import print_function, division
import textwrap
import numpy as np

from ..utils import listify 
from ..core.writable import Writable
from .variable import InputVariable

__all__ = ['AnaddbInput']


class AnaddbInput(Writable):
    """
    Anaddb input file.
    """

    def __init__(self, comment='', **kwargs):

        super(AnaddbInput, self).__init__(**kwargs)

        self.variables = dict()
        self.decimals = dict()
        self.comment = comment

    def set_comment(self, comment):
        """Write a comment for the input or for one dataset."""
        self.comment = comment

    def __str__(self):

        variables = list()

        for name, value in self.variables.items():
            variable = InputVariable(name, value,
                                     decimals=self.decimals.get(name, 0))

            variables.append(variable)

        lines = list()
        for variable in variables:
            svar = str(variable)
            if svar:
                lines.append(svar)

        return '\n'.join(lines) + '\n'


    def clear(self):
        """Clear variables."""
        self.variables.clear()

    def set_variable(self, name, value, decimals=None):
        """Set a single variable."""

        self.variables[name] = value
        if value is None:
            del self.variables[name]
            return
        if decimals is not None:
            self.decimals[name] = decimals

    def set_variables(self, variables, **kwargs):
        """
        Sets variables by providing a dictionary, or expanding a dictionary,
        and possibly append them by a dataset index.
        """
        #variables.update(kwargs)

        for (key, val) in variables.items():
            self.set_variable(key, val, **kwargs)

