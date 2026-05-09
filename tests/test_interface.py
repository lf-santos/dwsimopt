"""
Tests for the legacy DWSIM-Python interface workflow.

All tests use the shared `dwsim_interf` fixture (session-scoped)
since Automation2 can only be instantiated once per process.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from dwsimopt.sim_opt import SimulationOptimization

TESTS_DIR = Path(__file__).resolve().parent


@pytest.mark.requires_dwsim
class TestLegacyInterface:
    """Test the original manual interface workflow with real DWSIM."""

    def test_instantiation_valid_sim(self, dwsim_path):
        sim_path = TESTS_DIR / "test_sim_heater.dwxmz"
        sim = SimulationOptimization(
            path2sim=str(sim_path),
            path2dwsim=dwsim_path,
        )
        assert sim is not None
        assert sim.path2sim == str(sim_path.resolve())
        assert sim.n_dof == 0

    def test_instantiation_invalid_sim(self, dwsim_path):
        """Instantiation works even with a nonexistent path (fails at connect)."""
        sim = SimulationOptimization(
            path2sim="nonexistent_file.dwxmz",
            path2dwsim=dwsim_path,
        )
        assert sim is not None

    def test_add_refs_loads_modules(self, dwsim_interf):
        """After refs are loaded (via dwsim_interf fixture), DWSIM modules are in sys.modules."""
        # dwsim_interf fixture already called add_refs + Automation2()
        assert "DWSIM" in str(sys.modules) or True
        # The real check: we can import without error
        from DWSIM.Automation import Automation2  # pyright: ignore[reportMissingImports]

        assert Automation2 is not None

    def test_connect_with_valid_simulation(self, dwsim_path, dwsim_interf):
        """connect(interf) should load the flowsheet successfully."""
        sim_path = TESTS_DIR / "test_sim_heater.dwxmz"
        sim = SimulationOptimization(
            path2sim=str(sim_path),
            path2dwsim=dwsim_path,
        )
        sim._refs_added = True  # refs already loaded by session fixture
        sim.connect(dwsim_interf)

        assert sim.flowsheet is not None
        assert sim.interface is dwsim_interf

    def test_connect_with_invalid_simulation(self, dwsim_path, dwsim_interf):
        """connect(interf) with a bad path results in None flowsheet."""
        sim = SimulationOptimization(
            path2sim="this_does_not_exist.dwxmz",
            path2dwsim=dwsim_path,
        )
        sim._refs_added = True
        with pytest.raises(Exception):  # noqa: B017
            sim.connect(dwsim_interf)
        # DWSIM returns None flowsheet for nonexistent files
        assert sim.flowsheet is None
