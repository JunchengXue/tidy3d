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
    Boundary, Symmetry, PMLTypes
]

# boundary definition at the min and max coordinates along one dimension
Boundary1D = Tuple[BoundaryType, BoundaryType]


