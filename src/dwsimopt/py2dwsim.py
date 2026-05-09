"""
Python-DWSIM data exchange — create getter/setter functions for simulation objects.

This module provides the ``create_pddx`` and ``assign_pddx`` functions that generate
lambda-based getter/setter channels between Python and DWSIM simulation objects.

Backwards-compatible with the original ``dwsimopt.py2dwsim`` API.

.. module:: py2dwsim
   :synopsis: Data exchange from Python to DWSIM

:Author: Lucas F. Santos <lfs.francisco.95@gmail.com>
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

import numpy as np


def create_pddx(
    desc: list[str] | list[list[str]],
    sim: Any,
    element: str = "dof",
    assign: bool = True,
) -> list[Callable | None] | None:
    """Create a Python-DWSIM data exchange (pddx) channel.

    Generates getter or setter functions for DWSIM simulation objects and optionally
    assigns them to the optimization problem.

    Args:
        desc: Descriptor list ``[object_name, property, compound/phase, unit]``.
        sim: A :class:`~dwsimopt.sim_opt.SimulationOptimization` instance.
        element: Problem element type — ``'dof'``, ``'fobj'``, or ``'constraint'``.
        assign: If True, assign to ``sim``. If False, return the function(s).

    Returns:
        list of callables if ``assign=False``, otherwise None (assigned in-place).
    """
    m = np.shape(desc)

    if m[-1] < 2:
        raise ValueError(
            "desc must be [object_name (str), property (str), compound_or_phase (str), unit (str)]"
        )

    # Number of inputs
    n_inputs = m[0] if len(m) > 1 else 1

    ff: list[Callable | None] = []
    for ite in range(n_inputs):
        desc_ite: list[str] = cast(list[str], desc[ite] if n_inputs > 1 else desc)

        if element == "dof":
            f = _to_dwsim(desc_ite, sim)
        elif element in ("fobj", "constraint"):
            f = _from_dwsim(desc_ite, sim)
        else:
            raise ValueError(
                f"Unknown element type '{element}'. Use 'dof', 'fobj', or 'constraint'."
            )

        ff.append(f)

    if assign:
        assign_pddx(ff, desc, sim, element)
        return None
    else:
        if element == "dof":
            print(f"Created setter pddx for {desc[1]} of {desc[2]} from {desc[0]} in {desc[3]}")
        else:
            print(f"Created getter pddx for {desc[1]} of {desc[2]} from {desc[0]} in {desc[3]}")
        return cast(list[Callable | None], ff)


def assign_pddx(
    f: Any,
    desc: list[str] | list[list[str]],
    sim: Any,
    element: str = "dof",
) -> None:
    """Assign a pddx function to the simulation optimization object.

    Use this for custom objective/constraint functions built from basic pddx getters.

    Args:
        f: Function or list of functions to assign.
        desc: Descriptor list or list of descriptor lists.
        sim: :class:`~dwsimopt.sim_opt.SimulationOptimization` instance.
        element: ``'dof'``, ``'fobj'``, or ``'constraint'``.
    """
    n = np.size(f) if isinstance(f, (list, np.ndarray)) else 1
    funcs = [f] if n == 1 and callable(f) else f

    for ite in range(n):
        func = funcs[ite] if n > 1 else funcs[0]
        desc_ite: list[str] = cast(
            list[str],
            desc[ite] if isinstance(desc, list) and n > 1 and isinstance(desc[0], list) else desc,
        )

        if element == "dof":
            elem_add = sim.add_dof
            elem = sim.dof
            elem_n = sim.n_dof
        elif element == "fobj":
            elem_add = sim.add_fobj
            elem = sim.f
            elem_n = sim.n_f
        elif element == "constraint":
            elem_add = sim.add_constraint
            elem = sim.g
            elem_n = sim.n_g
        else:
            raise ValueError(f"Unknown element type '{element}'.")

        # Check for duplicates
        if elem.size == 0 or not _is_duplicate(elem, elem_n, desc_ite):
            elem_add(func, desc_ite)

        print(
            f"Added {element} pddx for {desc_ite[1]} of {desc_ite[2]} from {desc_ite[0]} in {desc_ite[3]}"
        )


def _is_duplicate(elem: np.ndarray, elem_n: int, desc: list[str]) -> bool:
    """Check if this descriptor already exists in the element array."""
    if elem_n == 1:
        rows = elem[1 : len(desc)]
        if np.all(np.array(desc[: len(desc) - 1], dtype=object) == rows):
            return True
    else:
        for row in elem:
            rows = row[1 : len(desc)]
            if np.all(np.array(desc[: len(desc) - 1], dtype=object) == rows):
                return True
    return False


def _to_dwsim(desc: list[str], sim: Any) -> Callable | None:
    """Create a setter function for a DWSIM object property.

    Args:
        desc: ``[object_name, property, compound/phase, unit]``.
        sim: Simulation object with a ``flowsheet`` attribute.

    Returns:
        Setter lambda, or None if property not recognized.
    """
    from DWSIM.SharedClasses.SystemsOfUnits import (  # pyright: ignore[reportMissingImports]
        Converter,
    )

    try:
        obj = sim.flowsheet.GetObject(desc[0]).GetAsObject()
    except Exception:
        print(f"Object '{desc[0]}' not found in simulation.")
        return None

    type_name = obj.GetType().FullName.split(".")
    setters: dict[str, Callable[[Any], None]] = {}

    # Material Stream
    if type_name[-1] == "MaterialStream":
        setters = {
            "MassFlow": lambda x: obj.SetMassFlow(f"{x} {desc[3]}"),
            "Temperature": lambda x: obj.SetTemperature(f"{x} {desc[3]}"),
            "Pressure": lambda x: obj.SetPressure(f"{x} {desc[3]}"),
            "MolarFlow": lambda x: obj.SetMolarFlow(f"{x} {desc[3]}"),
            "CompoundMassFlow": lambda x: obj.SetOverallCompoundMassFlow(
                desc[2], Converter.ConvertToSI(desc[3], x)
            ),
            "CompoundMolarFlow": lambda x: obj.SetOverallCompoundMolarFlow(
                desc[2], Converter.ConvertToSI(desc[3], x)
            ),
            # "CompoundMolarComposition": lambda x: obj.SetOverallCompoundMassFlow(
            #     desc[2], Converter.ConvertToSI(desc[3], x)
            # ),
        }
        f = setters.get(desc[1])
        if f is None:
            print(f"No setter for MaterialStream property '{desc[1]}'")
        return f

    # Energy Stream
    if type_name[-1] == "EnergyStream":
        setters = {
            "EnergyFlow": lambda x: _set_property(
                Converter.ConvertToSI(desc[3], x), obj, attr="EnergyFlow"
            ),
        }
        f = setters.get(desc[1])
        if f is None:
            print(f"No setter for EnergyStream property '{desc[1]}'")
        return f

    # Unit Operations
    if type_name[-2] == "UnitOperations":
        setters = {
            "OutletPressure": lambda x: _set_property(
                Converter.ConvertToSI(desc[3], x),
                obj,
                attr="POut" if type_name[-1] == "Compressor" else "OutletPressure",
            ),
            "OutletTemperature": lambda x: _set_property(
                Converter.ConvertToSI(desc[3], x), obj, attr="OutletTemperature"
            ),
        }
        f = setters.get(desc[1])
        if f is None:
            print(f"No setter for UnitOperation property '{desc[1]}'")
        return f

    print(f"Unrecognized object type for '{desc[0]}': {type_name[-1]}")
    print(f"Available properties: {list(setters.keys())}")
    return None


def _from_dwsim(desc: list[str], sim: Any) -> Callable | None:
    """Create a getter function for a DWSIM object property.

    Args:
        desc: ``[object_name, property, compound/phase, unit]``.
        sim: Simulation object with a ``flowsheet`` attribute.

    Returns:
        Getter lambda (no arguments), or None if not recognized.
    """
    from DWSIM.SharedClasses.SystemsOfUnits import (  # pyright: ignore[reportMissingImports]
        Converter,
    )

    try:
        obj = sim.flowsheet.GetObject(desc[0]).GetAsObject()
    except Exception:
        print(f"Object '{desc[0]}' not found in simulation.")
        return None

    type_name = obj.GetType().FullName.split(".")
    getters: dict[str, Callable[[], Any]] = {}

    # Phase index
    phase_map = {"Overall": 0, "Liquid": 1, "Vapor": 2}
    _phase = phase_map.get(desc[2], 0)

    # Material Stream
    if type_name[-1] == "MaterialStream":
        getters = {
            "MassFlow": lambda: Converter.ConvertFromSI(
                desc[3], obj.Phases[_phase].Properties.massflow
            ),
            "Temperature": lambda: Converter.ConvertFromSI(desc[3], obj.GetTemperature()),
            "Pressure": lambda: Converter.ConvertFromSI(desc[3], obj.GetPressure()),
            "MolarFlow": lambda: Converter.ConvertFromSI(
                desc[3], obj.Phases[_phase].Properties.molarflow
            ),
            "MassFraction": lambda: obj.Phases[_phase].Properties.massfraction,
            "MolarFraction": lambda: obj.Phases[_phase].Properties.molarfraction,
            "CompoundMassFlow": lambda: Converter.ConvertToSI(
                desc[3], obj.GetCompoundMassFlow(desc[2])
            ),
        }
        f = getters.get(desc[1])
        if f is None:
            print(f"No getter for MaterialStream property '{desc[1]}'")
        return f

    # Energy Stream
    if type_name[-1] == "EnergyStream":
        getters = {
            "EnergyFlow": lambda: Converter.ConvertFromSI(desc[3], obj.EnergyFlow),
        }
        f = getters.get(desc[1])
        if f is None:
            print(f"No getter for EnergyStream property '{desc[1]}'")
        return f

    # Unit Operations
    if type_name[-2] == "UnitOperations":
        getters = {
            "InputPressure": lambda: Converter.ConvertFromSI(
                desc[3], obj.PIn if type_name[-1] == "Compressor" else obj.InletPressure
            ),
            "InputTemperature": lambda: Converter.ConvertFromSI(desc[3], obj.InletTemperature),
            "OutletPressure": lambda: Converter.ConvertFromSI(
                desc[3], obj.POut if type_name[-1] == "Compressor" else obj.OutletPressure
            ),
            "OutletTemperature": lambda: Converter.ConvertFromSI(desc[3], obj.OutletTemperature),
            "OutputVariable": lambda: obj.OutputVariables[desc[2]],
            "InputVariables": lambda: obj.OutputVariables[desc[2]],
        }
        f = getters.get(desc[1])
        if f is None:
            print(f"No getter for UnitOperation property '{desc[1]}'")
        return f

    print(f"Unrecognized object type for '{desc[0]}': {type_name[-1]}")
    print(f"Available properties: {list(getters.keys())}")
    return None


def _set_property(x: Any, obj: Any, attr: str = "") -> None:
    """Helper: set an attribute on a .NET object."""
    setattr(obj, attr, x)
