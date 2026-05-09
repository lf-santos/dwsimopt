"""
Simulation optimization class — wraps a DWSIM simulation with DOFs, objectives, and constraints.

Backwards-compatible with the original ``dwsimopt.sim_opt.SimulationOptimization`` API.
Now inherits from :class:`~dwsimopt.simulation.DWSIMSimulation` to reuse connection logic.

.. module:: sim_opt
   :synopsis: DWSIM simulation optimization class

:Author: Lucas F. Santos <lfs.francisco.95@gmail.com>
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from dwsimopt.simulation import DWSIMSimulation


class SimulationOptimization(DWSIMSimulation):
    """DWSIM simulation wrapped with optimization problem definition.

    This class extends :class:`DWSIMSimulation` with degrees of freedom (DOF),
    objective functions, and constraints for simulation-based optimization.

    Backwards-compatible with the original v0.2 API. All old code that creates a
    ``SimulationOptimization`` instance will continue to work.

    Args:
        path2sim: Absolute path to a DWSIM simulation (.dwxmz).
        path2dwsim: Absolute path to DWSIM installation. Auto-detected if empty.
        savepath: Path to save the simulation. Defaults to ``path2sim``.
        verbose: Print status messages during simulation calculation.
        force_convergence: Retry calculations until results stabilize.
    """

    def __init__(
        self,
        path2sim: str,
        path2dwsim: str = "",
        savepath: str = "",
        verbose: bool = True,
        force_convergence: bool = True,
    ):  # pragma: no cover
        super().__init__(
            path_to_sim=path2sim,
            path_to_dwsim=path2dwsim,
            verbose=verbose,
        )
        # Keep legacy attribute names for backwards compatibility
        self.path2sim = self.path_to_sim
        self.path2dwsim = self.path_to_dwsim
        self.savepath = savepath if savepath else self.path_to_sim
        self.force_convergence = force_convergence

        # Optimization problem arrays
        self.x_val: np.ndarray = np.array([])
        self.f_val: np.ndarray = np.array([])
        self.g_val: np.ndarray = np.array([])
        self.f: np.ndarray = np.array([], dtype=object)
        self.n_f: int = 0
        self.g: np.ndarray = np.array([], dtype=object)
        self.n_g: int = 0
        self.dof: np.ndarray = np.array([], dtype=object)
        self.n_dof: int = 0

    # Keep legacy connect() signature working
    def connect(self, interf: Any = None) -> None:  # type: ignore[override]
        """Connect to a DWSIM flowsheet.

        Args:
            interf: Optional automation manager (legacy API). If None, creates one internally.
        """
        if interf is not None:
            # Legacy path: user passes an automation manager
            if not self._refs_added:
                self.add_refs()
            self.flowsheet = interf.LoadFlowsheet(self.path_to_sim)
            self.interface = interf
            if self.flowsheet is not None and self.verbose:
                print("Simulation was loaded successfully")
        else:
            # New path: use parent class connect()
            super().connect()

    def add_dof(self, dof_new: Any, description: list | None = None) -> None:
        """Append a new degree of freedom to the optimization problem.

        Args:
            dof_new: Callable (lambda/function) that sets a DOF value in DWSIM.
            description: Optional ``[object_name, property, compound/phase, unit]``.
        """
        desc = description if description is not None else [None, None, None, None]
        if self.dof.size == 0:
            self.dof = np.append(self.dof, np.append(dof_new, desc))
        else:
            self.dof = np.block([[self.dof], [np.append(dof_new, desc)]])
        self.n_dof += 1

    def add_fobj(self, func: Any, description: list | None = None) -> None:
        """Append a new objective function.

        Args:
            func: Callable that returns the objective value after simulation converges.
            description: Optional ``[object_name, property, compound/phase, unit]``.
        """
        desc = description if description is not None else [None, None, None, None]
        if self.f.size == 0:
            self.f = np.append(self.f, np.append(func, desc))
        else:
            self.f = np.block([[self.f], [np.append(func, desc)]])
        self.n_f += 1

    def add_constraint(self, g_func: Any, description: list | None = None) -> None:
        """Append a new constraint (g <= 0 convention).

        Args:
            g_func: Callable that returns the constraint value.
            description: Optional ``[object_name, property, compound/phase, unit]``.
        """
        desc = description if description is not None else [None, None, None, None]
        if self.g.size == 0:
            self.g = np.append(self.g, np.append(g_func, desc))
        else:
            self.g = np.block([[self.g], [np.append(g_func, desc)]])
        self.n_g += 1

    def converge_simulation(self, x: np.ndarray) -> None:
        """Assign DOF values and converge the simulation.

        If ``force_convergence`` is True, re-runs the simulation until outputs stabilize
        or a maximum of 5 total iterations is reached.

        Args:
            x: Array of DOF values to simulate.
        """
        if self.verbose:
            print(f"opt_functions calculation at x = {x}")

        n_assign = min(x.size, self.n_dof)
        if x.size != self.n_dof:
            print(
                f"Size of x ({x.size}) differs from n_dof ({self.n_dof}). "
                f"Only {n_assign} DOFs will be assigned."
            )

        # Assign DOF values
        if self.n_dof > 1:
            for i in range(n_assign):
                self.dof[i][0](x[i])
        elif self.n_dof == 1:
            self.dof[0](x[0])
        else:
            print(f"Converging simulation at x = {x} with 0 DOFs.")

        # First calculation
        error = self.interface.CalculateFlowsheet2(self.flowsheet)
        time.sleep(0.1)

        if not self.force_convergence:
            if error:
                print(f"{error} at x = {x}")
            return

        # Force convergence: re-run until stable
        error = self.interface.CalculateFlowsheet2(self.flowsheet)
        time.sleep(0.1)
        res_old = self._collect_results()

        for conv_ite in range(3):
            error = self.interface.CalculateFlowsheet2(self.flowsheet)
            time.sleep(0.1)
            res_new = self._collect_results()
            try:
                variation = np.linalg.norm(res_new - res_old)
            except (TypeError, ValueError):
                variation = 1.0
            if variation <= 1e-6:
                if self.verbose:
                    print(f"               Simulation converged in {conv_ite + 3} iterations")
                if error:
                    print(f"{error} at x = {x}")
                return
            res_old = res_new

        # Final attempt
        if error:
            error = self.interface.CalculateFlowsheet2(self.flowsheet)
            time.sleep(0.05)
            if self.verbose:
                print(
                    "               Simulation converged in 5 iterations or failed to converge..."
                )
            if error:
                print(f"{error} at x = {x}")

    def calculate_optProblem(self, x: np.ndarray) -> np.ndarray:
        """Converge the simulation and return objectives + constraints.

        Only re-runs if ``x`` differs from the last evaluated point.

        Args:
            x: Array of DOF values.

        Returns:
            Array of ``[f_values..., g_values...]``.
        """
        try:
            delta_x = np.linalg.norm(self.x_val - np.asarray(x))
        except (TypeError, ValueError):
            delta_x = 1.0

        if delta_x > 1e-10 or np.all(self.x_val == None):  # noqa: E711
            self.converge_simulation(x)
            self.x_val = np.array(x)
            self.f_val = self._evaluate_functions(self.f, self.n_f)
            self.g_val = self._evaluate_functions(self.g, self.n_g)

        if self.verbose:
            print(f"f = {self.f_val}, g = {self.g_val} at x = {x}")

        if self.n_g > 0:
            return np.append(self.f_val, self.g_val)
        return self.f_val

    def save_flowsheet(self) -> None:
        """Save the flowsheet to ``self.savepath``."""
        self.interface.SaveFlowsheet(self.flowsheet, self.savepath, True)

    # ─────────────────────────────────────────────────────────────
    # Penalization methods
    # ─────────────────────────────────────────────────────────────

    def fpen_barrier(self, x: np.ndarray, pen: float = 1000.0) -> float:
        """Penalized objective using barrier (linear) penalty on constraint violations.

        Args:
            x: DOF values.
            pen: Penalty parameter.

        Returns:
            Scalar penalized objective value.
        """
        self.calculate_optProblem(x)
        fpen = float(np.sum(self.f_val))
        for i in range(self.n_g):
            fpen += pen * max(0.0, self.g_val[i])
        return fpen

    def fpen_quad(self, x: np.ndarray, pen: float = 1000.0) -> float:
        """Penalized objective using quadratic penalty on constraint violations."""
        self.calculate_optProblem(x)
        fpen = float(np.sum(self.f_val))
        for i in range(self.n_g):
            fpen += pen * max(0.0, self.g_val[i]) ** 2
        return fpen

    def fpen_exp(self, x: np.ndarray, pen: float = 1000.0) -> float:
        """Penalized objective using exponential penalty on constraint violations."""
        import math

        self.calculate_optProblem(x)
        fpen = float(np.sum(self.f_val))
        for i in range(self.n_g):
            fpen += pen * math.exp(max(0.0, self.g_val[i]))
        return fpen

    # ─────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────

    def _collect_results(self) -> np.ndarray:
        """Collect current objective + constraint values for convergence check."""
        results = np.array([self.f[0]()] if self.n_f >= 1 else [0.0])
        for i in range(self.n_g):
            if self.n_g > 1:
                results = np.append(results, np.asarray(self.g[i][0]()))
            else:
                results = np.append(results, np.asarray(self.g[0]()))
        return results

    def _evaluate_functions(self, funcs: np.ndarray, n: int) -> np.ndarray | None:
        """Evaluate a set of objective or constraint functions."""
        if n == 0:
            return None
        values = np.zeros(n)
        if n > 1:
            for i in range(n):
                values[i] = funcs[i][0]()
        else:
            values[0] = funcs[0]()
        return values
