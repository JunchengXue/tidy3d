""" Tidy3d package imports"""
from concurrent.futures import ProcessPoolExecutor, process

import requests
from packaging.version import Version
from rich import pretty, traceback

# version
from .version import __version__

# pml
from .components import PML, StablePML, Absorber
from .components import PMLParams, AbsorberParams
from .components import DefaultPMLParameters, DefaultStablePMLParameters, DefaultAbsorberParameters

# grid
from .components import Grid, Coords

# geometry
from .components import Box, Sphere, Cylinder, PolySlab

# medium
from .components import Medium, PoleResidue, AnisotropicMedium, PEC, PECMedium
from .components import Sellmeier, Debye, Drude, Lorentz

# structures
from .components import Structure

# modes
from .components import ModeSpec

# sources
from .components import GaussianPulse, ContinuousWave
from .components import VolumeSource, PlaneWave, ModeSource, GaussianBeam

# monitors
from .components import FieldMonitor, FieldTimeMonitor, FluxMonitor, FluxTimeMonitor
from .components import ModeMonitor, ModeFieldMonitor

# simulation
from .components import Simulation

# data
from .components import SimulationData, FieldData, FluxData, FluxTimeData
from .components import DATA_TYPE_MAP, ScalarFieldData, ScalarFieldTimeData
from .components import ModeData, ModeAmpsData, ModeIndexData

# constants imported as `C_0 = td.C_0` or `td.constants.C_0`
from .constants import C_0, ETA_0, HBAR, EPSILON_0, MU_0, Q_e, inf

# plugins typically imported as `from tidy3d.plugins import DispersionFitter`
from . import plugins

# material library dict imported as `from tidy3d import material_library`
# get material `mat` and variant `var` as `material_library[mat][var]`
from .material_library import material_library

# logging
from .log import log, set_logging_level, set_logging_file

# for docs
from .components.medium import AbstractMedium
from .components.geometry import Geometry
from .components.source import Source, SourceTime
from .components.monitor import Monitor
from .components.grid import YeeGrid, FieldGrid, Coords1D

# make all stdout and errors pretty
pretty.install()
# traceback.install()

try:
    resp = requests.get("https://api.github.com/repos/flexcompute/tidy3d/releases/latest")
    json_resp = resp.json()
    tidy3d_version = Version(__version__)
    release_version = Version(json_resp["name"])
    if tidy3d_version < release_version:
        print(
            f"WARNING: You are using tidy3d version {tidy3d_version};"
            f" however, version {release_version} is available."
        )
        print(
            "You should consider upgrading via the 'python -m pip install --upgrade tidy3d' command"
        )
except Exception:  # pylint: disable=broad-except
    # silence if getting release information failed.
    pass
