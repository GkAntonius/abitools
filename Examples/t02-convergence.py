from pymatgen import Structure
from abitools import AbinitTask

# == Common Inputs == #
structure = Structure.from_file('Data/Structures/Si.json')

basis_set = {
    'ecut' : 15.,
    'ecutsm' : .5,
    }


kpoints = {
    'kptopt' : 1,
    'ngkpt' : [4, 4, 4],
    'nshiftk' : 4,
    'shiftk' : [[0.5, 0.5, 0.5],
                [0.5, 0.0, 0.0],
                [0.0, 0.5, 0.0],
                [0.0, 0.0, 0.5]],
    }

kpt_bs = {
    'kptopt' : -2,
    'ndivsm' : 20,
    'kptbounds' : [
        [.5, .5, .0],
        [.0, .0, .0],
        [.5, .0, .0],
        ],
    }

gstate = {
    'nstep' : 50,
    'tolvrs' : 1e-6,
    }

nband_occ = 4
nband_unocc = 4

wavefunctions = {
    'iscf' : -2,
    'irdden' : 1,
    #'getden' : 1,
    'nstep' : 50,
    'tolwfr' : 1e-12,
    'nband' : nband_occ + nband_unocc
    }

options = {
    'diemac' : 9.,
    }


# ================================================ #

# K-points grids for convergence study
kpt_grids = [
    [2,2,2],
    [3,3,3],
    [4,4,4],
    [6,6,6],
    ]

calcs = list()

for icalc, kpt_grid in enumerate(kpt_grids):

    calc = AbinitTask('02-Kptconv-{}'.format(icalc+1))

    # Number of processors
    calc.nproc = 4

    # Pseudopotentials
    calc.pseudo_dir = 'Data/Pseudos/'
    calc.pseudos = ['14-Si.pspnc']

    # Link the input of dataset 2 to the output of dataset 1 for the '_DEN' file
    calc.link_io(2, 1, 'DEN')
    
    # Set common variables
    calc.set_structure(structure)
    calc.set_variables(basis_set)
    calc.set_variables(options)
    calc.set_variables(gstate)
    calc.set_variables(kpoints)
    
    # Set varying variables
    calc.set_variables({'ngkpt' : kpt_grid})

    calcs.append(calc)


# Execution
for calc in calcs:
    calc.write()
    calc.run()
    calc.report()
