"""
Tests for the DWSIMSimulation connection layer.

These tests require DWSIM installed and are marked accordingly.
"""

import os

import pytest

from dwsimopt.simulation import DWSIMSimulation, find_dwsim_path


class TestFindDWSIMPath:
    """Test auto-detection of DWSIM path."""

    def test_returns_string(self):
        result = find_dwsim_path()
        assert isinstance(result, str)


@pytest.mark.requires_dwsim
class TestDWSIMSimulation:
    """Integration tests requiring DWSIM installation."""

    @pytest.fixture
    def sim(self):
        test_dir = os.path.dirname(__file__)
        sim_path = os.path.join(test_dir, "test_sim_heater.dwxmz")
        s = DWSIMSimulation(path_to_sim=sim_path, verbose=True)
        s.connect()
        return s

    def test_connect(self, sim):
        assert sim.flowsheet is not None
        assert sim.interface is not None

    def test_list_streams(self, sim):
        streams = sim.list_streams()
        assert isinstance(streams, dict)
        assert len(streams) > 0

    def test_list_unit_operations(self, sim):
        units = sim.list_unit_operations()
        assert isinstance(units, list)

    def test_list_compounds(self, sim):
        compounds = sim.list_compounds()
        assert isinstance(compounds, list)
        assert len(compounds) > 0

    def test_run(self, sim):
        result = sim.run()
        assert result is True
