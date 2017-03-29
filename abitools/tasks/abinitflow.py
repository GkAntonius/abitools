from __future__ import print_function
import os

from ..core import Workflow

__all__ = ['AbinitWorkflow']



class AbinitWorkflow(Workflow):

    def set_bindir(self, bindir):
        for task in self.tasks:
            task.set_bindir(bindir)

    def set_pseudo_dir(self, pseudo_dir):
        for task in self.tasks:
            task.pseudo_dir = pseudo_dir

    def set_pseudos(self, pseudos):
        for task in self.tasks:
            task.set_pseudos()
