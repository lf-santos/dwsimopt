"""
dwsimopt: DWSIM simulation automation and optimization with Python.

This package provides two main capabilities:
  1. **Simulation connection** (`DWSIMSimulation`) — load, configure, run, and read DWSIM flowsheets.
  2. **Simulation optimization** (`SimulationOptimization`, `OptimiSim`) — wrap a DWSIM simulation
     with degrees of freedom, objectives, and constraints for optimization.

Quick start:
    >>> from dwsimopt import DWSIMSimulation
    >>> sim = DWSIMSimulation("experiment.dwxmz")
    >>> sim.connect()
    >>> sim.run()

For optimization (backwards-compatible API):
    >>> from dwsimopt import SimulationOptimization, OptimiSim
"""

from .py2dwsim import assign_pddx, create_pddx
from .sim_opt import SimulationOptimization
from .simulation import DWSIMSimulation
from .solve_sim_opt import OptimiSim

__version__ = "1.0.0"

__all__ = [
    "DWSIMSimulation",
    "SimulationOptimization",
    "OptimiSim",
    "create_pddx",
    "assign_pddx",
]
