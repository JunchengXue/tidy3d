"""Defines boundary conditions"""
from typing import Union, Tuple, Literal
from abc import ABC

import pydantic

from .types import Symmetry
from .pml import PMLTypes
from .base import Tidy3dBaseModel


# class Boundary(Tidy3dBaseModel):


Boundary = Literal["PBC", "PEC", "PMC", "Bloch"]

# types of boundaries that are accepted by simulation
BoundaryType = Union[
    Boundary, PMLTypes
    ]

# boundary definition at the min and max coordinates along one dimension
Boundary1D = Union[
    Tuple[BoundaryType, BoundaryType]
    ]

# Logical constraints on Boundary1D:
# - If one entry is PBC, the other must also be PBC
# - If one entry is Bloch, the other must also be Bloch
# - If the BC is either PBC or Bloch, there cannot be a PML along that dimension
# - If the BC is either PBC or Bloch, there cannot be a symmetry specified along that dimension
# - PML overrides any non-periodic boundary conditions (PEC, PMC) along that dimension
# - PML, PEC, and PMC can be used in any combination
# - PEC and PMC are synonymous with symmetry once the domain is truncated

