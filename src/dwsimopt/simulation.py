"""
DWSIM Simulation Interface — Load, configure, run, and read DWSIM flowsheets.

This module provides a clean, focused interface for interacting with DWSIM simulations
without any optimization logic. It is the foundation on which optimization can be built.

Refactored from the original dwsim_interface.py into the dwsimopt package.

Requires:
  - DWSIM installed locally (Windows)
  - pythonnet (clr) and pywin32
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class StreamData:
    """Results extracted from a DWSIM material stream."""

    name: str
    temperature_K: float = 0.0  # noqa: N815
    pressure_Pa: float = 0.0  # noqa: N815
    mass_flow_kg_s: float = 0.0
    molar_flow_mol_s: float = 0.0
    enthalpy_kJ_kg: float = 0.0  # noqa: N815
    composition_mass: dict[str, float] = field(default_factory=dict)
    composition_molar: dict[str, float] = field(default_factory=dict)


@dataclass
class EnergyStreamData:
    """Results extracted from a DWSIM energy stream."""

    name: str
    energy_flow_kW: float = 0.0  # noqa: N815


def find_dwsim_path() -> str:
    """Auto-detect DWSIM installation path from system PATH environment variable.

    Returns:
        Path to DWSIM installation directory, or empty string if not found.
    """
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if "DWSIM" in entry.upper():
            return os.path.join(entry, "")
    return ""


class DWSIMSimulation:
    """
    Interface for loading, configuring, running, and reading DWSIM simulations.

    This class handles the .NET/COM interop with DWSIM and provides Pythonic
    getters/setters for streams and unit operations.

    Args:
        path_to_sim: Absolute or relative path to a DWSIM simulation file (.dwxmz).
        path_to_dwsim: Path to DWSIM installation. Auto-detected if empty.
        verbose: Print status messages during operations.

    Example:
        >>> sim = DWSIMSimulation("experiment.dwxmz")
        >>> sim.connect()
        >>> sim.set_stream_temperature("Feed", 350.0)
        >>> sim.run()
        >>> data = sim.get_stream_data("Product")
        >>> print(f"Product T = {data.temperature_K} K")
    """

    # Class-level automation manager (shared across instances)
    _automation_manager: Any = None

    def __init__(
        self,
        path_to_sim: str,
        path_to_dwsim: str = "",
        verbose: bool = True,
    ):
        self.path_to_sim = str(Path(path_to_sim).resolve())
        self.path_to_dwsim = path_to_dwsim or find_dwsim_path()
        self.verbose = verbose
        self.flowsheet: Any = None
        self.interface: Any = None
        self._refs_added = False

    def add_refs(self) -> None:
        """Add references to DWSIM .NET DLLs via pythonnet.

        Called automatically by :meth:`connect` if not done already.
        """
        import pythoncom

        pythoncom.CoInitialize()

        import clr

        dlls = [
            "CapeOpen.dll",
            "DWSIM.Automation.dll",
            "DWSIM.Interfaces.dll",
            "DWSIM.GlobalSettings.dll",
            "DWSIM.SharedClasses.dll",
            "DWSIM.Thermodynamics.dll",
            "DWSIM.UnitOperations.dll",
            "DWSIM.Inspector.dll",
            "DWSIM.MathOps.dll",
            "System.Buffers.dll",
            "TcpComm.dll",
            "Microsoft.ServiceBus.dll",
            "SkiaSharp.dll",
            "OxyPlot",
        ]

        for dll in dlls:
            dll_path = os.path.join(self.path_to_dwsim, dll)
            if os.path.exists(dll_path):
                clr.AddReference(dll_path)  # pyright: ignore[reportAttributeAccessIssue]
            elif self.verbose:
                print(f"  [skip] {dll} not found at {dll_path}")

        self._refs_added = True
        if self.verbose:
            print("DWSIM references added.")

    def connect(self) -> None:
        """Load the DWSIM flowsheet from file and store the automation interface.

        Raises:
            RuntimeError: If the flowsheet cannot be loaded.
        """
        if not self._refs_added:
            self.add_refs()

        from DWSIM.Automation import Automation3  # pyright: ignore[reportMissingImports]

        if DWSIMSimulation._automation_manager is None:
            DWSIMSimulation._automation_manager = Automation3()

        self.interface = DWSIMSimulation._automation_manager
        self.flowsheet = self.interface.LoadFlowsheet2(self.path_to_sim)

        if self.flowsheet is None:
            raise RuntimeError(f"Failed to load simulation: {self.path_to_sim}")

        if self.verbose:
            print(f"Loaded: {self.path_to_sim}")
            self._print_flowsheet_summary()

    def run(self, max_retries: int = 3, wait: float = 0.1) -> bool:
        """
        Calculate (solve) the flowsheet.

        Args:
            max_retries: Number of calculation attempts before giving up.
            wait: Seconds to wait between retries.

        Returns:
            True if converged without errors.

        Raises:
            RuntimeError: If not connected.
        """
        if self.flowsheet is None:
            raise RuntimeError("Not connected. Call connect() first.")

        for attempt in range(max_retries):
            errors = self.interface.CalculateFlowsheet2(self.flowsheet)
            time.sleep(wait)
            if not errors:
                if self.verbose:
                    print(f"  Simulation converged (attempt {attempt + 1})")
                return True
            if self.verbose:
                print(f"  Attempt {attempt + 1}: {errors}")

        if self.verbose:
            print("  WARNING: Simulation did not converge after retries.")
        return False

    def save(self, path: str | None = None) -> None:
        """Save the flowsheet to disk.

        Args:
            path: Target file path. Defaults to the original path_to_sim.
        """
        save_path = path or self.path_to_sim
        self.interface.SaveFlowsheet2(self.flowsheet, save_path)
        if self.verbose:
            print(f"  Saved: {save_path}")

    # ─────────────────────────────────────────────────────────────
    # SETTERS — Configure simulation inputs
    # ─────────────────────────────────────────────────────────────

    def set_stream_temperature(self, stream_name: str, T_K: float) -> None:  # noqa: N803
        """Set stream temperature in Kelvin."""
        obj = self._get_object(stream_name)
        obj.SetTemperature(str(T_K) + " K")

    def set_stream_pressure(self, stream_name: str, P_Pa: float) -> None:  # noqa: N803
        """Set stream pressure in Pascal."""
        obj = self._get_object(stream_name)
        obj.SetPressure(str(P_Pa) + " Pa")

    def set_stream_mass_flow(self, stream_name: str, flow_kg_s: float) -> None:
        """Set stream mass flow in kg/s."""
        obj = self._get_object(stream_name)
        obj.SetMassFlow(str(flow_kg_s) + " kg/s")

    def set_stream_molar_flow(self, stream_name: str, flow_mol_s: float) -> None:
        """Set stream molar flow in mol/s."""
        obj = self._get_object(stream_name)
        obj.SetMolarFlow(str(flow_mol_s) + " mol/s")

    def set_stream_composition(
        self, stream_name: str, composition: dict[str, float], basis: str = "mass"
    ) -> None:
        """
        Set stream composition.

        Args:
            stream_name: Name of the material stream in the flowsheet.
            composition: ``{compound_name: fraction}`` using DWSIM compound names.
            basis: ``"mass"`` or ``"molar"``.
        """
        obj = self._get_object(stream_name)

        if basis == "mass":
            for comp_name in self.flowsheet.SelectedCompounds.Keys:
                frac = composition.get(comp_name, 0.0)
                obj.Phases[0].Compounds[comp_name].MassFraction = frac
        elif basis == "molar":
            for comp_name in self.flowsheet.SelectedCompounds.Keys:
                frac = composition.get(comp_name, 0.0)
                obj.Phases[0].Compounds[comp_name].MoleFraction = frac
        else:
            raise ValueError(f"basis must be 'mass' or 'molar', got '{basis}'")

    def set_compound_mass_flow(self, stream_name: str, compound: str, flow_kg_s: float) -> None:
        """Set individual compound mass flow in a stream."""
        from DWSIM.SharedClasses.SystemsOfUnits import (  # pyright: ignore[reportMissingImports]
            Converter,
        )

        obj = self._get_object(stream_name)
        obj.SetOverallCompoundMassFlow(compound, Converter.ConvertToSI("kg/s", flow_kg_s))

    def set_compound_molar_flow(self, stream_name: str, compound: str, flow_mol_s: float) -> None:
        """Set individual compound molar flow in a stream."""
        from DWSIM.SharedClasses.SystemsOfUnits import (  # pyright: ignore[reportMissingImports]
            Converter,
        )

        obj = self._get_object(stream_name)
        obj.SetOverallCompoundMolarFlow(compound, Converter.ConvertToSI("mol/s", flow_mol_s))

    def set_unit_op_property(self, unit_name: str, property_name: str, value: float) -> None:
        """Set a numeric property on a unit operation by attribute name.

        Args:
            unit_name: Unit operation tag in the flowsheet.
            property_name: Attribute name (e.g., ``"OutletTemperature"``, ``"POut"``).
            value: Value in SI units.
        """
        obj = self._get_object(unit_name)
        setattr(obj, property_name, value)

    # ─────────────────────────────────────────────────────────────
    # GETTERS — Read simulation results
    # ─────────────────────────────────────────────────────────────

    def get_stream_data(self, stream_name: str) -> StreamData:
        """Read all key properties from a material stream.

        Args:
            stream_name: Name/tag of the material stream.

        Returns:
            :class:`StreamData` dataclass with temperature, pressure, flows, compositions.
        """
        obj = self._get_object(stream_name)
        phase = obj.Phases[0]  # Overall/mixed phase

        data = StreamData(
            name=stream_name,
            temperature_K=phase.Properties.temperature or 0.0,
            pressure_Pa=phase.Properties.pressure or 0.0,
            mass_flow_kg_s=phase.Properties.massflow or 0.0,
            molar_flow_mol_s=phase.Properties.molarflow or 0.0,
            enthalpy_kJ_kg=phase.Properties.enthalpy or 0.0,
        )

        for comp_name in self.flowsheet.SelectedCompounds.Keys:
            mf = phase.Compounds[comp_name].MassFraction
            xf = phase.Compounds[comp_name].MoleFraction
            if mf and mf > 0:
                data.composition_mass[comp_name] = mf
            if xf and xf > 0:
                data.composition_molar[comp_name] = xf

        return data

    def get_energy_stream_data(self, stream_name: str) -> EnergyStreamData:
        """Read energy flow from an energy stream."""
        obj = self._get_object(stream_name)
        return EnergyStreamData(
            name=stream_name,
            energy_flow_kW=getattr(obj, "EnergyFlow", 0.0),
        )

    def get_stream_property(self, stream_name: str, property_path: str) -> Any:
        """
        Get a specific property from a stream using dot/bracket notation.

        Args:
            stream_name: Stream tag.
            property_path: Dot-separated path, e.g. ``"Phases[0].Properties.temperature"``.

        Returns:
            The property value.
        """
        obj = self._get_object(stream_name)
        current: Any = obj
        for part in property_path.split("."):
            if "[" in part:
                attr, idx_str = part.split("[")
                idx = int(idx_str.rstrip("]"))
                current = getattr(current, attr)[idx]
            else:
                current = getattr(current, part)
        return current

    def get_unit_op_property(self, unit_name: str, property_name: str) -> Any:
        """Get a property value from a unit operation.

        Args:
            unit_name: Unit operation tag.
            property_name: Attribute name.

        Returns:
            The attribute value.
        """
        obj = self._get_object(unit_name)
        return getattr(obj, property_name)

    def get_output_variable(self, unit_name: str, variable_name: str) -> Any:
        """Read an output variable from a unit operation (e.g., a Python script block).

        Args:
            unit_name: Unit operation tag.
            variable_name: Key in ``OutputVariables`` dictionary.
        """
        obj = self._get_object(unit_name)
        return obj.OutputVariables[variable_name]

    def list_streams(self) -> dict[str, str]:
        """list all streams in the flowsheet with their types.

        Returns:
            dict mapping stream tag to its object type string.
        """
        streams: dict[str, str] = {}
        for obj in self.flowsheet.GraphicObjects.Values:
            obj_type = str(obj.ObjectType)
            if "MaterialStream" in obj_type or "EnergyStream" in obj_type:
                streams[obj.Tag] = obj_type
        return streams

    def list_unit_operations(self) -> list[str]:
        """list all unit operations in the flowsheet.

        Returns:
            list of strings in the format ``"Tag (ObjectType)"``.
        """
        units: list[str] = []
        for obj in self.flowsheet.GraphicObjects.Values:
            obj_type = str(obj.ObjectType)
            if "Stream" not in obj_type:
                units.append(f"{obj.Tag} ({obj_type})")
        return units

    def list_compounds(self) -> list[str]:
        """list all selected compounds in the flowsheet."""
        return list(self.flowsheet.SelectedCompounds.Keys)

    def get_object(self, name: str) -> Any:
        """Public access to a raw flowsheet simulation object by tag name.

        This gives full access to the underlying .NET object for advanced use cases.
        """
        return self._get_object(name)

    # ─────────────────────────────────────────────────────────────
    # INTERNAL HELPERS
    # ─────────────────────────────────────────────────────────────

    def _get_object(self, name: str) -> Any:
        """Get a flowsheet object by tag name."""
        obj = self.flowsheet.GetFlowsheetSimulationObject(name)
        if obj is None:
            available = [o.Tag for o in self.flowsheet.GraphicObjects.Values]
            raise KeyError(f"Object '{name}' not found. Available: {available}")
        return obj

    def _print_flowsheet_summary(self) -> None:
        """Print a summary of the loaded flowsheet."""
        streams = self.list_streams()
        units = self.list_unit_operations()
        compounds = self.list_compounds()
        print(f"  Streams: {len(streams)}")
        print(f"  Unit operations: {len(units)}")
        preview = ", ".join(compounds[:5])
        suffix = "..." if len(compounds) > 5 else ""
        print(f"  Compounds: {len(compounds)} ({preview}{suffix})")
