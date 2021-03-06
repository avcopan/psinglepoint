"""Module defining the molecule class.
"""
from psi4 import core

import numpy as np

from .parse import CoordinateString
from .util import atomdata, physconst


class Molecule(object):
    """A class to store information about a chemical system.                       
                                                                                   
    Attributes:                                                                    
      labels (`tuple` of `str`s): Atomic symbols.                                  
      coordinates (`np.ndarray`): An `self.natoms` x 3 array of Cartesian          
        coordinates corresponding to the atoms in `self.labels`.                   
      units (str): Either 'angstrom' or 'bohr', indicating the units of            
        `self.coordinates`.                                                        
    """

    @classmethod
    def from_psi4_molecule(cls, mol_psi4):
        mol_psi4.update_geometry()
        mol_str = mol_psi4.create_psi4_string_from_molecule()
        return cls.from_string(mol_str)

    @classmethod
    def from_string(cls, mol_str):
        coord_string = CoordinateString(mol_str)
        units = coord_string.extract_units()
        return cls.from_coord_string(coord_string, units)

    @classmethod
    def from_coord_string(cls, coord_string, units):
        labels = coord_string.extract_labels()
        coordinates = coord_string.extract_coordinates()
        return cls(labels, coordinates, units)

    def __init__(self, labels, coordinates, units="angstrom"):
        """Initialize this Molecule object.                                          
        """
        self.labels = tuple(labels)
        self.coordinates = np.array(coordinates)
        self.units = str(units.lower())
        self.masses = [atomdata.get_mass(label) for label in labels]
        self.natom = len(labels)
        if self.units not in ("angstrom", "bohr"):
            raise ValueError("Units must be 'angstrom' or 'bohr'.")

    def set_units(self, units):
        if units == "angstrom" and self.units == "bohr":
            self.units = "angstrom"
            self.coordinates *= physconst.bohr2angstrom
        elif units == "bohr" and self.units == "angstrom":
            self.units = "bohr"
            self.coordinates /= physconst.bohr2angstrom

    def __iter__(self):
        for label, xyz in zip(self.labels, self.coordinates):
            yield label, xyz

    def __str__(self):
        ret = "units {:s}\n".format(self.units)
        fmt = "{:2s} {: >15.10f} {: >15.10f} {: >15.10f}\n"
        for label, coords in self:
            ret += fmt.format(label, *coords)
        return ret

    def __repr__(self):
        return str(self)

    def copy(self):
        return Molecule(self.labels, self.coordinates.copy(), self.units)

    def set_coordinates(self, coordinates, units=None):
        if units is None:
            units = self.units
        self.units = units
        self.coordinates = coordinates

    def make_psi4_molecule_object(self):
        core.efp_init()
        mol_psi4 = core.Molecule.create_molecule_from_string(str(self))
        mol_psi4.update_geometry()
        return mol_psi4


if __name__ == "__main__":
    mol_string = """
units angstrom
  O  0.0000000000  0.0000000000 -0.0647162893
  H  0.0000000000 -0.7490459967  0.5135472375
  H  0.0000000000  0.7490459967  0.5135472375
"""
    mol = Molecule.from_string(mol_string)
    print(mol.units)
    print(mol.labels)
    print(mol.coordinates)
