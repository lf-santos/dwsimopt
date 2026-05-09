"""
Tests for OptimiSim — the high-level optimizer.

Covers:
  - Instantiation without auto-init
  - _get_penalty_func dispatch
  - _validate_problem checks
  - _default_pop / _default_max_ite helpers
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from dwsimopt.solve_sim_opt import OptimiSim


class TestOptimiSimInstantiation:
    def test_no_auto_init(self, tmp_path):
        f = tmp_path / "sim.dwxmz"
        f.touch()
        sim = OptimiSim(path2sim=str(f), path2dwsim="/d/", init_dwsim=False)
        assert sim.n_dof == 0
        assert sim.flowsheet is None

    def test_inherits_sim_opt(self, tmp_path):
        f = tmp_path / "sim.dwxmz"
        f.touch()
        sim = OptimiSim(path2sim=str(f), path2dwsim="/d/", init_dwsim=False)
        assert hasattr(sim, "add_dof")
        assert hasattr(sim, "fpen_barrier")
        assert hasattr(sim, "calculate_optProblem")


class TestPenaltyFuncDispatch:
    @pytest.fixture
    def sim(self, tmp_path):
        f = tmp_path / "sim.dwxmz"
        f.touch()
        s = OptimiSim(path2sim=str(f), path2dwsim="/d/", init_dwsim=False)
        s.interface = MagicMock()
        s.interface.CalculateFlowsheet2.return_value = ""
        s.flowsheet = MagicMock()
        s._refs_added = True
        s.add_dof(lambda x: None)
        s.add_fobj(lambda: 10.0)
        s.force_convergence = False
        return s

    def test_barrier(self, sim):
        assert callable(sim._get_penalty_func("barrier", 100.0))

    def test_quad(self, sim):
        assert callable(sim._get_penalty_func("quad", 100.0))

    def test_exp(self, sim):
        assert callable(sim._get_penalty_func("exp", 100.0))

    def test_unknown_raises(self, sim):
        with pytest.raises(ValueError, match="Unknown penalization"):
            sim._get_penalty_func("banana", 100.0)


class TestValidateProblem:
    def test_no_objective_raises(self, tmp_path):
        f = tmp_path / "sim.dwxmz"
        f.touch()
        sim = OptimiSim(path2sim=str(f), path2dwsim="/d/", init_dwsim=False)
        with pytest.raises(ValueError, match="No objective"):
            sim._validate_problem()

    def test_multi_objective_raises(self, tmp_path):
        f = tmp_path / "sim.dwxmz"
        f.touch()
        sim = OptimiSim(path2sim=str(f), path2dwsim="/d/", init_dwsim=False)
        sim.add_fobj(lambda: 1.0)
        sim.add_fobj(lambda: 2.0)
        with pytest.raises(NotImplementedError, match="Multi-objective"):
            sim._validate_problem()

    def test_single_objective_ok(self, tmp_path):
        f = tmp_path / "sim.dwxmz"
        f.touch()
        sim = OptimiSim(path2sim=str(f), path2dwsim="/d/", init_dwsim=False)
        sim.add_fobj(lambda: 1.0)
        sim._validate_problem()  # should not raise


class TestDefaultPopMaxIte:
    @pytest.fixture
    def sim(self, tmp_path):
        f = tmp_path / "sim.dwxmz"
        f.touch()
        s = OptimiSim(path2sim=str(f), path2dwsim="/d/", init_dwsim=False)
        s.add_dof(lambda x: None)
        s.add_dof(lambda x: None)
        s.add_dof(lambda x: None)  # n_dof = 3
        return s

    def test_default_pop(self, sim):
        assert sim._default_pop([]) == 6  # 2*3

    def test_custom_pop(self, sim):
        assert sim._default_pop(20) == 20

    def test_default_max_ite(self, sim):
        assert sim._default_max_ite([]) == 15  # 5*3

    def test_custom_max_ite(self, sim):
        assert sim._default_max_ite(50) == 50

    def test_zero_pop_uses_default(self, sim):
        assert sim._default_pop(0) == 6

    def test_negative_pop_uses_default(self, sim):
        assert sim._default_pop(-5) == 6
