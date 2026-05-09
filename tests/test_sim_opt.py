"""
Tests for SimulationOptimization class.

Covers:
  - Instantiation and defaults
  - add_dof / add_fobj / add_constraint
  - converge_simulation (mocked)
  - calculate_optProblem caching
  - Penalization methods (barrier, quad, exp)
  - Legacy connect() signature
"""

from __future__ import annotations

import math
from unittest.mock import MagicMock

import numpy as np
import pytest

from dwsimopt.sim_opt import SimulationOptimization


class TestSimOptInstantiation:
    def test_defaults(self, tmp_path):
        f = tmp_path / "sim.dwxmz"
        f.touch()
        sim = SimulationOptimization(path2sim=str(f), path2dwsim="/d/")
        assert sim.n_dof == 0
        assert sim.n_f == 0
        assert sim.n_g == 0
        assert sim.force_convergence is True

    def test_legacy_attributes(self, tmp_path):
        f = tmp_path / "sim.dwxmz"
        f.touch()
        sim = SimulationOptimization(path2sim=str(f), path2dwsim="/opt/")
        assert sim.path2sim == sim.path_to_sim
        assert sim.path2dwsim == sim.path_to_dwsim

    def test_savepath_defaults(self, tmp_path):
        f = tmp_path / "sim.dwxmz"
        f.touch()
        sim = SimulationOptimization(path2sim=str(f), path2dwsim="/d/")
        assert sim.savepath == sim.path_to_sim

    def test_custom_savepath(self, tmp_path):
        f = tmp_path / "sim.dwxmz"
        f.touch()
        sim = SimulationOptimization(path2sim=str(f), path2dwsim="/d/", savepath="/tmp/out.dwxmz")
        assert sim.savepath == "/tmp/out.dwxmz"


class TestAddDOF:
    def test_single(self, sim_opt_with_mocks):
        sim_opt_with_mocks.add_dof(lambda x: x)
        assert sim_opt_with_mocks.n_dof == 1

    def test_multiple(self, sim_opt_with_mocks):
        sim_opt_with_mocks.add_dof(lambda x: x)
        sim_opt_with_mocks.add_dof(lambda x: x * 2)
        sim_opt_with_mocks.add_dof(lambda x: x * 3)
        assert sim_opt_with_mocks.n_dof == 3

    def test_with_description(self, sim_opt_with_mocks):
        sim_opt_with_mocks.add_dof(lambda x: x, description=["S1", "T", "Mix", "K"])
        assert sim_opt_with_mocks.dof[1] == "S1"

    def test_callable(self, sim_opt_with_mocks):
        results = []
        sim_opt_with_mocks.add_dof(lambda x: results.append(x))
        sim_opt_with_mocks.dof[0](42.0)
        assert results == [42.0]


class TestAddFobj:
    def test_single(self, sim_opt_with_mocks):
        sim_opt_with_mocks.add_fobj(lambda: 99.0)
        assert sim_opt_with_mocks.n_f == 1

    def test_multiple(self, sim_opt_with_mocks):
        sim_opt_with_mocks.add_fobj(lambda: 1.0)
        sim_opt_with_mocks.add_fobj(lambda: 2.0)
        assert sim_opt_with_mocks.n_f == 2

    def test_callable(self, sim_opt_with_mocks):
        sim_opt_with_mocks.add_fobj(lambda: 3.14)
        assert sim_opt_with_mocks.f[0]() == 3.14


class TestAddConstraint:
    def test_single(self, sim_opt_with_mocks):
        sim_opt_with_mocks.add_constraint(lambda: -1.0)
        assert sim_opt_with_mocks.n_g == 1

    def test_multiple(self, sim_opt_with_mocks):
        sim_opt_with_mocks.add_constraint(lambda: -1.0)
        sim_opt_with_mocks.add_constraint(lambda: 0.5)
        assert sim_opt_with_mocks.n_g == 2

    def test_callable(self, sim_opt_with_mocks):
        sim_opt_with_mocks.add_constraint(lambda: -2.5)
        assert sim_opt_with_mocks.g[0]() == -2.5


class TestConvergeSimulation:
    def test_single_dof_assigned(self, sim_opt_with_mocks):
        values = []
        sim_opt_with_mocks.add_dof(lambda x: values.append(x))
        sim_opt_with_mocks.add_fobj(lambda: 0.0)
        sim_opt_with_mocks.force_convergence = False
        sim_opt_with_mocks.converge_simulation(np.array([5.0]))
        assert values == [5.0]

    def test_multiple_dof_assigned(self, sim_opt_with_mocks):
        vals = {}
        sim_opt_with_mocks.add_dof(lambda x: vals.update({"a": x}))
        sim_opt_with_mocks.add_dof(lambda x: vals.update({"b": x}))
        sim_opt_with_mocks.add_fobj(lambda: 0.0)
        sim_opt_with_mocks.force_convergence = False
        sim_opt_with_mocks.converge_simulation(np.array([1.0, 2.0]))
        assert vals == {"a": 1.0, "b": 2.0}

    def test_calls_calculate_flowsheet(self, sim_opt_with_mocks):
        sim_opt_with_mocks.add_dof(lambda x: None)
        sim_opt_with_mocks.add_fobj(lambda: 0.0)
        sim_opt_with_mocks.force_convergence = False
        sim_opt_with_mocks.converge_simulation(np.array([1.0]))
        sim_opt_with_mocks.interface.CalculateFlowsheet2.assert_called()

    def test_force_convergence_retries(self, sim_opt_with_mocks):
        sim_opt_with_mocks.add_dof(lambda x: None)
        sim_opt_with_mocks.add_fobj(lambda: 42.0)
        sim_opt_with_mocks.force_convergence = True
        sim_opt_with_mocks.converge_simulation(np.array([1.0]))
        assert sim_opt_with_mocks.interface.CalculateFlowsheet2.call_count >= 2


class TestCalculateOptProblem:
    def test_fobj_only(self, sim_opt_with_mocks):
        sim_opt_with_mocks.add_dof(lambda x: None)
        sim_opt_with_mocks.add_fobj(lambda: 7.0)
        sim_opt_with_mocks.force_convergence = False
        result = sim_opt_with_mocks.calculate_optProblem(np.array([1.0]))
        np.testing.assert_array_almost_equal(result, [7.0])

    def test_fobj_and_constraints(self, sim_opt_with_mocks):
        sim_opt_with_mocks.add_dof(lambda x: None)
        sim_opt_with_mocks.add_fobj(lambda: 10.0)
        sim_opt_with_mocks.add_constraint(lambda: -1.0)
        sim_opt_with_mocks.add_constraint(lambda: 0.5)
        sim_opt_with_mocks.force_convergence = False
        result = sim_opt_with_mocks.calculate_optProblem(np.array([1.0]))
        np.testing.assert_array_almost_equal(result, [10.0, -1.0, 0.5])

    def test_caches_same_x(self, sim_opt_with_mocks):
        counter = {"n": 0}
        sim_opt_with_mocks.add_dof(lambda x: counter.update(n=counter["n"] + 1))
        sim_opt_with_mocks.add_fobj(lambda: 1.0)
        sim_opt_with_mocks.force_convergence = False
        sim_opt_with_mocks.calculate_optProblem(np.array([5.0]))
        sim_opt_with_mocks.calculate_optProblem(np.array([5.0]))
        assert counter["n"] == 1

    def test_recalculates_on_new_x(self, sim_opt_with_mocks):
        counter = {"n": 0}
        sim_opt_with_mocks.add_dof(lambda x: counter.update(n=counter["n"] + 1))
        sim_opt_with_mocks.add_fobj(lambda: 1.0)
        sim_opt_with_mocks.force_convergence = False
        sim_opt_with_mocks.calculate_optProblem(np.array([1.0]))
        sim_opt_with_mocks.calculate_optProblem(np.array([2.0]))
        assert counter["n"] == 2


class TestPenalization:
    @pytest.fixture
    def sim_with_problem(self, sim_opt_with_mocks):
        sim_opt_with_mocks.add_dof(lambda x: None)
        sim_opt_with_mocks.add_fobj(lambda: 5.0)
        sim_opt_with_mocks.add_constraint(lambda: 2.0)   # violated
        sim_opt_with_mocks.add_constraint(lambda: -1.0)  # satisfied
        sim_opt_with_mocks.force_convergence = False
        return sim_opt_with_mocks

    def test_barrier_violated(self, sim_with_problem):
        # 5 + 100*max(0,2) + 100*max(0,-1) = 5 + 200 = 205
        assert sim_with_problem.fpen_barrier(np.array([1.0]), pen=100.0) == pytest.approx(205.0)

    def test_barrier_all_satisfied(self, sim_opt_with_mocks):
        sim_opt_with_mocks.add_dof(lambda x: None)
        sim_opt_with_mocks.add_fobj(lambda: 3.0)
        sim_opt_with_mocks.add_constraint(lambda: -1.0)
        sim_opt_with_mocks.force_convergence = False
        assert sim_opt_with_mocks.fpen_barrier(np.array([1.0]), pen=1000.0) == pytest.approx(3.0)

    def test_quad_violated(self, sim_with_problem):
        # 5 + 100*2^2 + 100*0 = 405
        assert sim_with_problem.fpen_quad(np.array([1.0]), pen=100.0) == pytest.approx(405.0)

    def test_exp_violated(self, sim_with_problem):
        expected = 5.0 + 100.0 * math.exp(2.0) + 100.0 * math.exp(0.0)
        assert sim_with_problem.fpen_exp(np.array([1.0]), pen=100.0) == pytest.approx(expected)


class TestLegacyConnect:
    def test_connect_with_interface(self, sim_opt_with_mocks, mock_interface):
        sim_opt_with_mocks.flowsheet = None
        mock_interface.LoadFlowsheet2.return_value = MagicMock()
        sim_opt_with_mocks.connect(mock_interface)
        assert sim_opt_with_mocks.flowsheet is not None
        assert sim_opt_with_mocks.interface is mock_interface

    def test_connect_loads_correct_path(self, sim_opt_with_mocks, mock_interface):
        sim_opt_with_mocks.flowsheet = None
        mock_interface.LoadFlowsheet2.return_value = MagicMock()
        sim_opt_with_mocks.connect(mock_interface)
        mock_interface.LoadFlowsheet2.assert_called_with(sim_opt_with_mocks.path_to_sim)


class TestSaveFlowsheet:
    def test_calls_save(self, sim_opt_with_mocks):
        sim_opt_with_mocks.save_flowsheet()
        sim_opt_with_mocks.interface.SaveFlowsheet2.assert_called_once_with(
            sim_opt_with_mocks.flowsheet, sim_opt_with_mocks.savepath, True
        )
