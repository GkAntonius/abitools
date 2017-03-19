from pymatgen import Structure
from abitools import AbinitTask

# Initialize the Launcher.
calc = AbinitTask('01-Bandstructure')

# Structure
calc.set_structure(Structure.from_file('Data/Structures/Si.json'))

# Pseudopotentials
calc.pseudo_dir = 'Data/Pseudos/'
calc.pseudos = ['14-Si.pspnc']

# Executable
#calc.set_bindir('/path/to/abinit/binaries/src/98_main/')

# Number of processors for execution
calc.nproc = 4

# == Inputs == #

basis_set = {
    'ecut' : 15.,
    'ecutsm' : .5,
    }


kpt_grid = {
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
    'nstep' : 20,
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

# Link the input of dataset 2 to the output of dataset 1 for the '_DEN' file
calc.link_io(2, 1, 'DEN')

# Set common variables
calc.set_variables(basis_set)
calc.set_variables(options)

# Set data-specific variables
calc.ndtset = 2
calc.set_variables(gstate, 1)
calc.set_variables(kpt_grid, 1)
calc.set_variables(wavefunctions, 2)
calc.set_variables(kpt_bs, 2)

# Add some comments
calc.set_comment('A band structure calculation')
calc.set_comment('Ground state', 1)
calc.set_comment('Wavefunctions', 2)

# Write the files, run the calculation, and report the status.
calc.write()
calc.run()
calc.report()

