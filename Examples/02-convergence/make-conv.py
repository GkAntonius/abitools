from abitools import MassLauncher

# Initialize a MassLauncher composed of 4 calculations
calc = MassLauncher(4, 'Kptconv-')

# We will use these k-points grids
kpt_grids = [
    [2,2,2],
    [3,3,3],
    [4,4,4],
    [6,6,6],
    ]


# Pseudopotentials
calc.set_pseudodir('../Data/Pseudos/')
calc.set_pseudos(['14-Si.pspnc'])

# Executable
#calc.set_bindir('/path/to/abinit/binaries/src/98_main/')


# Job setting
nproc = 4

# Set the mpi command used to run abinit.
calc.set_mpirun('mpirun -np {} '.format(nproc))


# == Inputs == #

unitcell = {
    'acell' : 3*[10.263],
    'rprim' : [[0.0,0.5,0.5],
               [0.5,0.0,0.5],
               [0.5,0.5,0.0]],
    'ntypat' : 1,
    'znucl' : 14,
    'natom' : 2,
    'typat' : [1,1],
    'xred' : [3*[0.0], 3*[0.25]]
    }


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
    'nstep' : 50,
    'tolvrs' : 1e-14,
    }

nband_occ = 4
nband_unocc = 4

wavefunctions = {
    'iscf' : -2,
    'irdden' : 1,
    #'getden' : 1,
    'nstep' : 50,
    'tolwfr' : 1e-18,
    'nband' : nband_occ + nband_unocc
    }

options = {
    'diemac' : 9.,
    }


# Link the input of dataset 2 to the output of dataset 1 for the '_DEN' file
calc.link_io(2, 1, 'DEN')

# Set common variables
calc.set_variables(unitcell)
calc.set_variables(basis_set)
calc.set_variables(options)
calc.set_variables(gstate)
calc.set_variables(kpt_grid)

# Set varying variables
calc.set_variables(kpt_grid)

for i, c in enumerate(calc):
    c.set_variables({'ngkpt' : kpt_grids[i]})

# Write the file and overwrite them if they exist.
calc.make(force=True)

