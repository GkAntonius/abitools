from __future__ import print_function, division
import numpy as np

from ..utils.units import angstrom_to_bohr

#import pymatgen

__all__ = ['structure_to_abivars']

def structure_to_abivars(structure):
    """Get abinit variables from a pymatgen.Structure object."""

    rprim = structure.lattice.matrix * angstrom_to_bohr

    xred = list()
    for site in structure.sites:
        xred.append(site.frac_coords.round(14).tolist())

    natom = structure.num_sites
    ntypat = structure.ntypesp

    znucl_atom = structure.atomic_numbers

    itypat = 0
    typat = list()
    znucl = list()
    for z in znucl_atom:
        if z not in znucl:
            itypat += 1
            znucl.append(z)
            typat.append(itypat)
        else:
            i = znucl.index(z)
            typat.append(i+1)

    d = dict(
        rprim=rprim.tolist(),
        acell=np.ones(3, dtype=float).tolist(),
        natom=natom,
        ntypat=ntypat,
        znucl=znucl,
        typat=typat,
        xred=xred,
        )

    return d
