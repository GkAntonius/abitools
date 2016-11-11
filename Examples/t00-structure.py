"""
Construct a Structure object using pymatgen and write the structure file.

See http://pymatgen.org/ for more information.
"""
import numpy as np
import pymatgen

# Construct the structure object.
acell_angstrom =  5.6535
rprim = np.array([[.0,.5,.5],[.5,.0,.5],[.5,.5,.0]]) * acell_angstrom
structure = pymatgen.Structure(
    lattice = pymatgen.core.lattice.Lattice(rprim),
    species= ['Ga', 'As'],
    coords = [3*[.0], 3*[.25]],
    )

# Write file in Crystallographic Information Framework.
# This the format defined by the International Union of Crystallography.
structure.to(filename='00-GaAs.cif')

# Write in json format. This is the prefered format
# since it preserves the above definition of the unit cell.
structure.to(filename='00-GaAs.json')

