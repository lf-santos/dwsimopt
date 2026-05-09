"""
High-level optimizer class that auto-initializes DWSIM and provides solver methods.

Backwards-compatible with the original ``dwsimopt.solve_sim_opt.OptimiSim`` API.

.. module:: solve_sim_opt
   :synopsis: Class to solve DWSIM simulation optimization problems

:Author: Lucas F. Santos <lfs.francisco.95@gmail.com>
"""

from __future__ import annotations

from typing import Any

import numpy as np

from dwsimopt.sim_opt import SimulationOptimization


class OptimiSim(SimulationOptimization):
    """All-in-one optimizer that auto-connects to DWSIM on instantiation.

    Inherits all DOF/objective/constraint machinery from :class:`SimulationOptimization`
    and adds meta-heuristic solvers (PSO, GA, DE, AFSA) via ``scikit-opt``.

    Args:
        path2sim: Absolute path to a DWSIM simulation (.dwxmz).
        path2dwsim: Path to DWSIM installation. Auto-detected if empty.
        savepath: Path to save the simulation.
        verbose: Print status messages.
        force_convergence: Retry calculations until stable.
        init_dwsim: If True, auto-detect DWSIM path, add refs, and connect on init.
    """

    def __init__(
        self,
        path2sim: str,
        path2dwsim: str = "",
        savepath: str = "",
        verbose: bool = True,
        force_convergence: bool = True,
        init_dwsim: bool = True,
    ):
        super().__init__(
            path2sim=path2sim,
            path2dwsim=path2dwsim,
            savepath=savepath,
            verbose=verbose,
            force_convergence=force_convergence,
        )  # pragma: no cover

        if init_dwsim:
            self._auto_init()

    def _auto_init(self) -> None:
        """Auto-detect DWSIM, add references, and connect."""

        if not self.path_to_dwsim:
            from dwsimopt.simulation import find_dwsim_path

            self.path_to_dwsim = find_dwsim_path()
            self.path2dwsim = self.path_to_dwsim

        if not self.path_to_dwsim:
            self.path_to_dwsim = input(
                r"Please input the path to your DWSIM installation "
                r"(e.g. C:\Users\UserName\AppData\Local\DWSIM8): "
            )
            if self.path_to_dwsim and self.path_to_dwsim[-1] not in "\\/":
                self.path_to_dwsim += "/"
            self.path2dwsim = self.path_to_dwsim

        self.add_refs()

        from DWSIM.Automation import Automation2

        if DWSIMSimulation._automation_manager is None:
            from dwsimopt.simulation import DWSIMSimulation

            DWSIMSimulation._automation_manager = Automation2()

        self.interface = DWSIMSimulation._automation_manager
        self.connect(self.interface)

    # ─────────────────────────────────────────────────────────────
    # Penalization helper (DRY)
    # ─────────────────────────────────────────────────────────────

    def _get_penalty_func(self, pen_method: str, pen_factor: float):
        """Return the penalized objective function for the given method."""
        methods = {
            "barrier": self.fpen_barrier,
            "quad": self.fpen_quad,
            "exp": self.fpen_exp,
        }
        if pen_method not in methods:
            raise ValueError(
                f"Unknown penalization method '{pen_method}'. Choose from: {list(methods.keys())}"
            )
        return lambda x: methods[pen_method](x, pen=pen_factor)

    def _default_pop(self, pop: int | list) -> int:
        return pop if isinstance(pop, int) and pop > 0 else 2 * self.n_dof

    def _default_max_ite(self, max_ite: int | list) -> int:
        return max_ite if isinstance(max_ite, int) and max_ite > 0 else 5 * self.n_dof

    # ─────────────────────────────────────────────────────────────
    # Solvers
    # ─────────────────────────────────────────────────────────────

    def PSO(
        self,
        x0: np.ndarray,
        xlb: np.ndarray,
        xub: np.ndarray,
        pen_method: str = "barrier",
        pen_factor: float = 1000.0,
        pop: int | list | None = None,
        max_ite: int | list | None = None,
        verbose: bool = True,
        plotting: bool = True,
    ) -> Any:
        """Particle Swarm Optimization.

        Args:
            x0: Initial guess (used for sizing, not as start point for PSO).
            xlb: Lower bounds for DOFs.
            xub: Upper bounds for DOFs.
            pen_method: Penalization method (``'barrier'``, ``'quad'``, ``'exp'``).
            pen_factor: Penalty multiplier.
            pop: Population size (default: ``2 * n_dof``).
            max_ite: Maximum iterations (default: ``5 * n_dof``).
            verbose: Print progress.
            plotting: Plot convergence history.

        Returns:
            ``sko.PSO.PSO`` result object.
        """
        from sko.PSO import PSO

        if max_ite is None:
            max_ite = []
        if pop is None:
            pop = []
        self._validate_problem()
        f_pen = self._get_penalty_func(pen_method, pen_factor)
        _pop = self._default_pop(pop)
        _max_ite = self._default_max_ite(max_ite)

        result = PSO(
            func=f_pen,
            n_dim=self.n_dof,
            pop=_pop,
            max_iter=_max_ite,
            lb=xlb,
            ub=xub,
            verbose=verbose,
        )
        result.record_mode = True
        print("Starting PSO optimization")
        result.run()

        if plotting:
            self._plot_convergence(result.gbest_y_hist, "PSO")
            self._print_solution(result.gbest_x, "PSO")

        return result

    def GA(
        self,
        x0: np.ndarray,
        xlb: np.ndarray,
        xub: np.ndarray,
        pen_method: str = "barrier",
        pen_factor: float = 1000.0,
        pop: int | list | None = None,
        max_ite: int | list | None = None,
        prob_mut: float | list | None = None,
        verbose: bool = True,
        plotting: bool = True,
    ) -> Any:
        """Genetic Algorithm.

        Args:
            x0: Initial guess.
            xlb: Lower bounds.
            xub: Upper bounds.
            pen_method: Penalization method.
            pen_factor: Penalty multiplier.
            pop: Population size.
            max_ite: Maximum iterations.
            prob_mut: Mutation probability (default: 0.5).
            verbose: Print progress.
            plotting: Plot convergence.

        Returns:
            ``sko.GA.GA`` result object.
        """
        from sko.GA import GA

        if prob_mut is None:
            prob_mut = []
        if max_ite is None:
            max_ite = []
        if pop is None:
            pop = []
        self._validate_problem()
        f_pen = self._get_penalty_func(pen_method, pen_factor)
        _pop = self._default_pop(pop)
        _max_ite = self._default_max_ite(max_ite)
        _prob_mut = prob_mut if isinstance(prob_mut, float) and prob_mut > 0 else 0.5

        result = GA(
            func=f_pen,
            n_dim=self.n_dof,
            size_pop=_pop,
            max_iter=_max_ite,
            prob_mut=_prob_mut,
            lb=xlb,
            ub=xub,
        )
        result.record_mode = True
        print("Starting GA optimization")
        result.run()

        if plotting:
            self._plot_convergence(result.generation_best_Y, "GA")
            self._print_solution(result.best_x, "GA")

        return result

    def DE(
        self,
        x0: np.ndarray,
        xlb: np.ndarray,
        xub: np.ndarray,
        pen_method: str = "barrier",
        pen_factor: float = 1000.0,
        pop: int | list | None = None,
        max_ite: int | list | None = None,
        verbose: bool = True,
        plotting: bool = True,
    ) -> Any:
        """Differential Evolution.

        Args:
            x0: Initial guess.
            xlb: Lower bounds.
            xub: Upper bounds.
            pen_method: Penalization method.
            pen_factor: Penalty multiplier.
            pop: Population size.
            max_ite: Maximum iterations.
            verbose: Print progress.
            plotting: Plot convergence.

        Returns:
            ``sko.DE.DE`` result object.
        """
        from sko.DE import DE

        if max_ite is None:
            max_ite = []
        if pop is None:
            pop = []
        self._validate_problem()
        f_pen = self._get_penalty_func(pen_method, pen_factor)
        _pop = self._default_pop(pop)
        _max_ite = self._default_max_ite(max_ite)

        result = DE(
            func=f_pen,
            n_dim=self.n_dof,
            size_pop=_pop,
            max_iter=_max_ite,
            lb=xlb,
            ub=xub,
        )
        result.record_mode = True
        print("Starting DE optimization")
        result.run()

        if plotting:
            self._plot_convergence(result.generation_best_Y, "DE")
            self._print_solution(result.best_x, "DE")

        return result

    def AFSA(
        self,
        x0: np.ndarray,
        pen_method: str = "barrier",
        pen_factor: float = 1000.0,
        pop: int | list | None = None,
        max_ite: int | list | None = None,
        verbose: bool = True,
        plotting: bool = True,
        max_try_num: int = 100,
        step: float = 0.5,
        visual: float = 0.3,
        q: float = 0.98,
        delta: float = 0.5,
    ) -> Any:
        """Artificial Fish Swarm Algorithm.

        Args:
            x0: Initial guess.
            pen_method: Penalization method.
            pen_factor: Penalty multiplier.
            pop: Population size.
            max_ite: Maximum iterations.
            verbose: Print progress.
            plotting: Plot convergence.
            max_try_num: Max try number per fish.
            step: Step size.
            visual: Visual range.
            q: Contraction factor.
            delta: Crowd factor.

        Returns:
            ``sko.AFSA.AFSA`` result object.
        """
        from sko.AFSA import AFSA

        if max_ite is None:
            max_ite = []
        if pop is None:
            pop = []
        self._validate_problem()
        f_pen = self._get_penalty_func(pen_method, pen_factor)
        _pop = self._default_pop(pop)
        _max_ite = self._default_max_ite(max_ite)

        result = AFSA(
            func=f_pen,
            n_dim=self.n_dof,
            size_pop=_pop,
            max_iter=_max_ite,
            max_try_num=max_try_num,
            step=step,
            visual=visual,
            q=q,
            delta=delta,
        )
        result.record_mode = True
        print("Starting AFSA optimization")
        result.run()

        return result

    # ─────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────

    def _validate_problem(self) -> None:
        """Check that the optimization problem is well-defined."""
        if self.n_f > 1:
            raise NotImplementedError("Multi-objective optimization not supported (yet).")
        if self.n_f < 1:
            raise ValueError("No objective function defined. Call add_fobj() first.")

    def _print_solution(self, best_x: np.ndarray, solver_name: str) -> None:
        """Print the solution at the optimum."""
        print(f"{solver_name} finished with x* = {best_x}")
        self.converge_simulation(best_x)
        if self.n_f >= 1:
            if self.n_f > 1:
                for i in range(self.n_f):
                    print(f"  f_{i} = {self.f[i][0]()}")
            else:
                print(f"  fobj = {self.f[0]()}")
        for i in range(self.n_g):
            if self.n_g > 1:
                print(f"  g_{i} = {self.g[i][0]()}")
            else:
                print(f"  g_0 = {self.g[0]()}")

    def _plot_convergence(self, history: Any, solver_name: str) -> None:
        """Plot optimization convergence history."""
        try:
            import matplotlib.pyplot as plt

            plt.figure()
            plt.plot(history)
            plt.xlabel("Iteration")
            plt.ylabel("Best Objective")
            plt.title(f"{solver_name} Convergence")
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
        except ImportError:
            print("matplotlib not available — skipping convergence plot.")
