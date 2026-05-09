"""
Tests for DWSIMSimulation — the simulation connection layer.

Unit tests use mocks. Integration tests use the shared dwsim_interf fixture.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from dwsimopt.simulation import (
    DWSIMSimulation,
    EnergyStreamData,
    StreamData,
    find_dwsim_path,
)

# ─── Unit Tests (no DWSIM required) ──────────────────────────────────────────


class TestFindDWSIMPath:
    def test_returns_string(self):
        assert isinstance(find_dwsim_path(), str)

    def test_finds_dwsim_when_in_path(self, monkeypatch):
        monkeypatch.setenv("PATH", "/usr/bin:/opt/DWSIM8:/usr/local/bin")
        assert "DWSIM" in find_dwsim_path().upper()

    def test_returns_empty_when_not_in_path(self, monkeypatch):
        monkeypatch.setenv("PATH", "/usr/bin:/usr/local/bin")
        assert find_dwsim_path() == ""


class TestStreamDataDataclasses:
    def test_stream_data_defaults(self):
        sd = StreamData(name="test")
        assert sd.temperature_K == 0.0
        assert sd.composition_mass == {}

    def test_stream_data_custom(self):
        sd = StreamData(name="Feed", temperature_K=350.0, composition_mass={"Water": 0.8})
        assert sd.temperature_K == 350.0
        assert sd.composition_mass["Water"] == 0.8

    def test_independent_instances(self):
        sd1 = StreamData(name="s1")
        sd2 = StreamData(name="s2")
        sd1.composition_mass["Water"] = 1.0
        assert "Water" not in sd2.composition_mass

    def test_energy_stream_defaults(self):
        assert EnergyStreamData(name="Q").energy_flow_kW == 0.0


class TestDWSIMSimulationInit:
    def test_basic(self, tmp_path):
        f = tmp_path / "test.dwxmz"
        f.touch()
        sim = DWSIMSimulation(path_to_sim=str(f), path_to_dwsim="/opt/dwsim/")
        assert sim.path_to_sim == str(f.resolve())
        assert sim.flowsheet is None
        assert sim._refs_added is False

    def test_path_resolved(self, tmp_path):
        f = tmp_path / "sub" / "sim.dwxmz"
        f.parent.mkdir()
        f.touch()
        sim = DWSIMSimulation(path_to_sim=str(f))
        assert Path(sim.path_to_sim).is_absolute()

    def test_auto_detect(self, monkeypatch, tmp_path):
        f = tmp_path / "sim.dwxmz"
        f.touch()
        monkeypatch.setenv("PATH", "/opt/DWSIM8:/usr/bin")
        sim = DWSIMSimulation(path_to_sim=str(f), path_to_dwsim="")
        assert "DWSIM" in sim.path_to_dwsim.upper()

    def test_run_raises_without_connect(self, tmp_path):
        f = tmp_path / "sim.dwxmz"
        f.touch()
        sim = DWSIMSimulation(path_to_sim=str(f), path_to_dwsim="/d/")
        with pytest.raises(RuntimeError, match="Not connected"):
            sim.run()


class TestDWSIMSimulationWithMocks:
    @pytest.fixture
    def sim_with_mock(self, tmp_path, mock_flowsheet, mock_interface):
        f = tmp_path / "sim.dwxmz"
        f.touch()
        sim = DWSIMSimulation(path_to_sim=str(f), path_to_dwsim="/dummy/")
        sim.flowsheet = mock_flowsheet
        sim.interface = mock_interface
        sim._refs_added = True
        return sim

    def test_run_success(self, sim_with_mock):
        sim_with_mock.interface.CalculateFlowsheet2.return_value = ""
        assert sim_with_mock.run(max_retries=1, wait=0.0) is True

    def test_run_failure(self, sim_with_mock):
        sim_with_mock.interface.CalculateFlowsheet2.return_value = "Error"
        assert sim_with_mock.run(max_retries=2, wait=0.0) is False

    def test_run_retries_then_succeeds(self, sim_with_mock):
        sim_with_mock.interface.CalculateFlowsheet2.side_effect = ["error", ""]
        assert sim_with_mock.run(max_retries=3, wait=0.0) is True

    def test_save_default(self, sim_with_mock):
        sim_with_mock.save()
        sim_with_mock.interface.SaveFlowsheet.assert_called_once_with(
            sim_with_mock.flowsheet, sim_with_mock.path_to_sim, True
        )

    def test_save_custom(self, sim_with_mock, tmp_path):
        p = str(tmp_path / "out.dwxmz")
        sim_with_mock.save(path=p)
        sim_with_mock.interface.SaveFlowsheet.assert_called_once_with(
            sim_with_mock.flowsheet, p, True
        )

    def test_set_stream_temperature(self, sim_with_mock):
        obj = sim_with_mock.flowsheet.GetFlowsheetSimulationObject.return_value
        sim_with_mock.set_stream_temperature("Feed", 400.0)
        obj.SetTemperature.assert_called_once_with("400.0 K")

    def test_set_stream_pressure(self, sim_with_mock):
        obj = sim_with_mock.flowsheet.GetFlowsheetSimulationObject.return_value
        sim_with_mock.set_stream_pressure("Feed", 200000.0)
        obj.SetPressure.assert_called_once_with("200000.0 Pa")

    def test_set_stream_mass_flow(self, sim_with_mock):
        obj = sim_with_mock.flowsheet.GetFlowsheetSimulationObject.return_value
        sim_with_mock.set_stream_mass_flow("Feed", 2.5)
        obj.SetMassFlow.assert_called_once_with("2.5 kg/s")

    def test_set_unit_op_property(self, sim_with_mock):
        obj = sim_with_mock.flowsheet.GetFlowsheetSimulationObject.return_value
        sim_with_mock.set_unit_op_property("H1", "OutletTemperature", 450.0)
        assert obj.OutletTemperature == 450.0

    def test_get_object_raises_on_missing(self, sim_with_mock):
        sim_with_mock.flowsheet.GetFlowsheetSimulationObject.return_value = None
        with pytest.raises(KeyError, match="not found"):
            sim_with_mock._get_object("X")

    def test_list_compounds(self, sim_with_mock):
        assert sim_with_mock.list_compounds() == ["Water", "Methane", "Ethane"]

    def test_invalid_basis_raises(self, sim_with_mock):
        with pytest.raises(ValueError, match="basis must be"):
            sim_with_mock.set_stream_composition("Feed", {"Water": 1.0}, basis="vol")


# ─── Integration Tests ────────────────────────────────────────────────────────


@pytest.mark.requires_dwsim
class TestDWSIMSimulationIntegration:
    """End-to-end tests using the shared dwsim_interf fixture."""

    @pytest.fixture
    def sim(self, test_sim_heater_path, dwsim_path, dwsim_interf):
        s = DWSIMSimulation(
            path_to_sim=str(test_sim_heater_path),
            path_to_dwsim=dwsim_path,
        )
        # Use the shared interface instead of creating a new one
        s._refs_added = True
        s.interface = dwsim_interf
        s.flowsheet = dwsim_interf.LoadFlowsheet(s.path_to_sim)
        return s

    def test_connect_loads_flowsheet(self, sim):
        assert sim.flowsheet is not None

    def test_list_streams_nonempty(self, sim):
        assert len(sim.list_streams()) > 0

    def test_list_unit_operations_nonempty(self, sim):
        assert len(sim.list_unit_operations()) > 0
