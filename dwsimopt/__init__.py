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

from dwsimopt.simulation import DWSIMSimulation
from dwsimopt.sim_opt import SimulationOptimization
from dwsimopt.solve_sim_opt import OptimiSim
from dwsimopt.py2dwsim import create_pddx, assign_pddx

__version__ = "1.0.0"

__all__ = [
    "DWSIMSimulation",
    "SimulationOptimization",
    "OptimiSim",
    "create_pddx",
    "assign_pddx",
]
