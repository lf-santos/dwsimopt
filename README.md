# dwsimopt: DWSIM simulation & optimization with Python

[![PyPI](https://img.shields.io/pypi/v/dwsimopt)](https://pypi.org/project/dwsimopt/)
[![Python](https://img.shields.io/pypi/pyversions/dwsimopt)](https://pypi.org/project/dwsimopt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docs](https://readthedocs.org/projects/pydwsimopt/badge/?version=latest)](https://pydwsimopt.readthedocs.io)

A Python package for automating [DWSIM](https://dwsim.org) process simulations and solving
simulation-based optimization problems.

## What's New in v0.3.0

- **Separated concerns**: Simulation connection (`DWSIMSimulation`) is now independent of
  optimization (`SimulationOptimization`, `OptimiSim`).
- **Modern packaging**: Uses `pyproject.toml` with `hatchling` build backend. Compatible with
  `uv`, `pip`, and `pipx`.
- **Python 3.9+**: Dropped Python 3.8 support; uses modern type hints.
- **Optional dependencies**: Core package only needs `numpy`. Install `[optimization]` or
  `[dwsim]` extras as needed.
- **100% backwards compatible**: Existing code using `SimulationOptimization` or `OptimiSim`
  works without changes.

## Installation

```bash
# With uv (recommended)
uv add dwsimopt

# With pip
pip install dwsimopt

# With all extras (optimization solvers + DWSIM bindings)
uv add "dwsimopt[all]"
pip install "dwsimopt[all]"

# Development
uv add "dwsimopt[dev]"
```

## Quick Start

### Simulation only (new API)

```python
from dwsimopt import DWSIMSimulation

sim = DWSIMSimulation("experiment.dwxmz")
sim.connect()

# Configure inputs
sim.set_stream_temperature("Feed", 350.0)
sim.set_stream_mass_flow("Feed", 1.5)
sim.set_unit_op_property("Heater-1", "OutletTemperature", 400.0)

# Run
sim.run()

# Read results
product = sim.get_stream_data("Product")
print(f"Product T = {product.temperature_K} K")
print(f"Product flow = {product.mass_flow_kg_s} kg/s")

energy = sim.get_energy_stream_data("Q-Heater")
print(f"Heat duty = {energy.energy_flow_kW} kW")
```

### Simulation optimization (backwards-compatible)

```python
from dwsimopt import OptimiSim
import numpy as np

# Auto-connects to DWSIM
sim = OptimiSim(path2sim="experiment.dwxmz")

# Define optimization problem
sim.add_dof(lambda x: sim.flowsheet.GetFlowsheetSimulationObject("Feed").SetTemperature(f"{x} K"))
sim.add_fobj(lambda: sim.flowsheet.GetFlowsheetSimulationObject("Q-Heater").EnergyFlow)
sim.add_constraint(lambda: 400 - sim.flowsheet.GetFlowsheetSimulationObject("Product").GetTemperature())

# Solve with PSO
result = sim.PSO(
    x0=np.array([350.0]),
    xlb=np.array([300.0]),
    xub=np.array([500.0]),
    plotting=True,
)
```

### Using py2dwsim data exchange (backwards-compatible)

```python
from dwsimopt import SimulationOptimization, create_pddx

sim = SimulationOptimization(path2sim="experiment.dwxmz", path2dwsim="/path/to/DWSIM/")
sim.add_refs()

from DWSIM.Automation import Automation2
interf = Automation2()
sim.connect(interf)

# Declarative DOF setup
create_pddx(["Feed", "Temperature", "Mixture", "K"], sim, element="dof")
create_pddx(["Heater", "EnergyFlow", "Mixture", "kW"], sim, element="fobj")
```

## Architecture

```
dwsimopt/
├── simulation.py      # DWSIMSimulation — connection, run, get/set (no optimization)
├── sim_opt.py         # SimulationOptimization — adds DOF/obj/constraints on top
├── solve_sim_opt.py   # OptimiSim — auto-init + solver methods (PSO, GA, DE, AFSA)
├── py2dwsim.py        # Declarative getter/setter factory (create_pddx)
└── utils.py           # Shared utilities
```

**Inheritance chain:**

```
DWSIMSimulation  →  SimulationOptimization  →  OptimiSim
(connection)        (problem definition)       (solvers)
```

## Requirements

- Python ≥ 3.9
- DWSIM installed (Windows) for simulation execution
- `numpy` (core dependency)
- `scikit-opt` (optional, for optimization solvers)
- `pythonnet` ≥ 3.0 (optional, for DWSIM .NET interop)

## License

MIT License — see [LICENSE](LICENSE).

## Citing us

If you use dwsimopt, please cite the following paper: <a href="https://doi.org/10.1016/j.apenergy.2022.118537" title="simulation optimization paper">L. F. Santos, C. B. B. Costa, J. A. Caballero, M. A. S. S. Ravagnani, Framework for embedding black-box simulation into mathematical programming via kriging surrogate model applied to natural gas liquefaction process optimization, Applied Energy, 310, 118537 (2022).</a>

<pre>
@article{Santos2022,
title = {Framework for embedding black-box simulation into mathematical programming via kriging surrogate model applied to natural gas liquefaction process optimization},
author = {Lucas F. Santos and Caliane B.B. Costa and José A. Caballero and Mauro A.S.S. Ravagnani},
journal = {Applied Energy},
volume = {310},
pages = {118537},
year = {2022},
issn = {0306-2619},
doi = {https://doi.org/10.1016/j.apenergy.2022.118537},
</pre>