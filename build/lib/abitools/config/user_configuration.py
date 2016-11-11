"""
The user is advised to set the default behavior
of the module to their needs.

IMPORTANT:
Within this directory, copy this file as follow:
    cp  user_configuration.py.template  user_configuration.py

Then, edit the file user_configuration.py as desired.
This should be done before installing the module with the setup script.
"""

# MPI parameters
# Some mpi runners specify the number of processors and number of proc. per node,
# while other specify the number of nodes and the number of proc. per node.
# To disable a feature, set the value or the flag to None.
default_mpi = dict(
    mpirun = 'mpirun',
    nproc = 4,
    nproc_flag = '-n',
    nproc_per_node = 1,
    nproc_per_node_flag = None,
    nodes = 1,
    nodes_flag = None,
    )


# General options for the bash script used to run Abinit.
default_runscript = dict(
    first_line = '#!/bin/bash', # The first line appearing in run scripts.
                                # Do not use any other shell than bash.

    header = [],                # Preemble lines that appear befor the main
                                # execution of all runscripts.
                                # Can be used, e.g. to load modules.

    footer = [],                # Lines that appear at the end of the scripts.
    )


