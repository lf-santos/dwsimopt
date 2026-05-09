"""
Tests for SimulationOptimization (backwards compatibility).
"""

import os

import numpy as np
import pytest

from dwsimopt.sim_opt import SimulationOptimization


class TestSimulationOptimizationUnit:
    """Unit tests that don't require DWSIM."""

    def test_instantiation(self):
        sim = SimulationOptimization(path2sim="dummy.dwxmz", path2dwsim="/dummy")
        assert sim.n_dof == 0
        assert sim.n_f == 0
        assert sim.n_g == 0
        assert sim.path2sim == sim.path_to_sim
        assert sim.verbose is True

    def test_add_dof(self):
        sim = SimulationOptimization(path2sim="dummy.dwxmz", path2dwsim="/dummy")
        sim.add_dof(lambda x: x)
        assert sim.n_dof == 1
        sim.add_dof(lambda x: x * 2)
        assert sim.n_dof == 2

    def test_add_fobj(self):
        sim = SimulationOptimization(path2sim="dummy.dwxmz", path2dwsim="/dummy")
        sim.add_fobj(lambda: 42.0)
        assert sim.n_f == 1

    def test_add_constraint(self):
        sim = SimulationOptimization(path2sim="dummy.dwxmz", path2dwsim="/dummy")
        sim.add_constraint(lambda: -1.0)
        assert sim.n_g == 1


@pytest.mark.requires_dwsim
class TestSimulationOptimizationIntegration:
    """Integration tests requiring DWSIM."""

    @pytest.fixture
    def sim_smr(self):
        test_dir = os.path.dirname(__file__)
        sim_path = os.path.join(test_dir, "test_sim.dwxmz")
        path2dwsim = ""
        for entry in os.environ.get("PATH", "").split(os.pathsep):
            if "DWSIM" in entry.upper():
                path2dwsim = os.path.join(entry, "")
                break

        sim = SimulationOptimization(path2sim=sim_path, path2dwsim=path2dwsim)
        sim.add_refs()

        from DWSIM.Automation import Automation2

        interf = Automation2()
        sim.connect(interf)
        return sim

    def test_reproducibility(self, sim_smr):
        sim_smr.add_dof(
            lambda x: sim_smr.flowsheet.GetFlowsheetSimulationObject("MR-1")
            .SetOverallCompoundMassFlow(7, x)
        )
        sim_smr.add_fobj(
            lambda: sim_smr.flowsheet.GetFlowsheetSimulationObject("Sum_W").EnergyFlow
        )

        x0 = np.array([0.25 / 3600])
        f1 = sim_smr.calculate_optProblem(x0)
        f2 = sim_smr.calculate_optProblem(1.1 * x0)
        f3 = sim_smr.calculate_optProblem(x0)

        assert not np.allclose(f1, f2)
        np.testing.assert_array_almost_equal(f1, f3)
