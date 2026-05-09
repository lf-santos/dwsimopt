"""
Pytest configuration and shared fixtures for dwsimopt tests.

All path handling uses pathlib.Path.

IMPORTANT: DWSIM's Automation2 can only be instantiated once per process.
The `dwsim_interf` fixture (session-scoped) provides the single shared instance.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from dotenv import load_dotenv

# ─── Directory constants ──────────────────────────────────────────────────────

TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent


# ─── DWSIM availability check ────────────────────────────────────────────────


def _find_dwsim_in_path() -> str:
    """Search system PATH for a DWSIM directory."""
    for entry in os.environ.get("PATH", "").split(os.pathsep)[-1]:
        if "DWSIM" in entry.upper():
            return entry
    load_dotenv(override=True)
    path2dwsim = os.getenv("PATH2DWSIM", "")
    if path2dwsim:
        return path2dwsim
    return ""


def _dwsim_is_installed() -> bool:
    """Check if DWSIM is installed by verifying the automation DLL exists on disk."""
    dwsim_dir = _find_dwsim_in_path()
    if not dwsim_dir:
        dwsim_dir = os.environ.get("DWSIM_PATH", "")
    if not dwsim_dir:
        return False
    automation_dll = Path(dwsim_dir) / "DWSIM.Automation.dll"
    return automation_dll.is_file()


# ─── Pytest configuration ─────────────────────────────────────────────────────


def pytest_configure(config):
    config.addinivalue_line("markers", "requires_dwsim: marks tests that need DWSIM installed")


def pytest_collection_modifyitems(config, items):
    """Auto-skip tests marked requires_dwsim when DWSIM is not installed."""
    if not _dwsim_is_installed():
        skip_marker = pytest.mark.skip(
            reason="DWSIM not installed (DWSIM.Automation.dll not found)"
        )
        for item in items:
            if "requires_dwsim" in item.keywords:
                item.add_marker(skip_marker)


# ─── Path fixtures ────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def dwsim_path() -> str:
    """Return the DWSIM installation path with trailing separator."""
    path = _find_dwsim_in_path()
    if not path:
        path = os.environ.get("DWSIM_PATH", "")
    if path and not path.endswith(os.sep):
        path += os.sep
    return path


@pytest.fixture
def test_sim_heater_path() -> Path:
    """Path to the heater test simulation file."""
    return TESTS_DIR / "test_sim_heater.dwxmz"


@pytest.fixture
def test_sim_path() -> Path:
    """Path to the SMR test simulation file."""
    return TESTS_DIR / "test_sim.dwxmz"


# ─── DWSIM session fixture (single Automation2 instance) ─────────────────────


@pytest.fixture(scope="session")
def dwsim_interf(dwsim_path):
    """Session-scoped DWSIM Automation2 instance.

    Automation2 can only be instantiated ONCE per process. This fixture
    ensures all tests share the same instance.
    """
    from dwsimopt.simulation import DWSIMSimulation

    # Create a temporary sim object just to load refs
    sim = DWSIMSimulation.__new__(DWSIMSimulation)
    sim.path_to_dwsim = dwsim_path
    sim.verbose = False
    sim._refs_added = False
    sim.add_refs()

    from DWSIM.Automation import Automation2  # pyright: ignore[reportMissingImports]

    interf = Automation2()
    return interf


# ─── Mock fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def mock_interface() -> MagicMock:
    """A mocked DWSIM Automation2 interface."""
    interf = MagicMock()
    interf.CalculateFlowsheet2.return_value = ""
    interf.LoadFlowsheet.return_value = MagicMock()
    interf.SaveFlowsheet.return_value = None
    return interf


@pytest.fixture
def mock_flowsheet() -> MagicMock:
    """A mocked DWSIM flowsheet object."""
    flowsheet = MagicMock()
    flowsheet.SelectedCompounds.Keys = ["Water", "Methane", "Ethane"]
    flowsheet.GraphicObjects.Values = []
    mock_obj = MagicMock()
    flowsheet.GetFlowsheetSimulationObject.return_value = mock_obj
    return flowsheet


@pytest.fixture
def sim_opt_with_mocks(tmp_path, mock_flowsheet, mock_interface):
    """A SimulationOptimization instance with mocked flowsheet/interface."""
    from dwsimopt.sim_opt import SimulationOptimization

    sim_file = tmp_path / "test.dwxmz"
    sim_file.touch()
    sim = SimulationOptimization(path2sim=str(sim_file), path2dwsim="/mock/dwsim/")
    sim.flowsheet = mock_flowsheet
    sim.interface = mock_interface
    sim._refs_added = True
    return sim
