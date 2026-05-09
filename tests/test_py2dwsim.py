"""
Tests for py2dwsim — Python-DWSIM data exchange factory.

Covers:
  - create_pddx validation
  - _is_duplicate helper
  - assign_pddx deduplication
"""

from __future__ import annotations

import numpy as np
import pytest

from dwsimopt.py2dwsim import _is_duplicate, assign_pddx, create_pddx


class TestCreatePddxValidation:
    def test_desc_too_short_raises(self, sim_opt_with_mocks):
        with pytest.raises(ValueError, match="desc must be"):
            create_pddx(["only_one"], sim_opt_with_mocks, element="dof")

    def test_invalid_element_raises(self, sim_opt_with_mocks):
        with pytest.raises(ValueError, match="Unknown element type"):
            create_pddx(["A", "B", "C", "D"], sim_opt_with_mocks, element="invalid")


class TestIsDuplicate:
    def test_empty_not_duplicate(self):
        assert _is_duplicate(np.array([], dtype=object), 0, ["A", "B", "C", "D"]) is False

    def test_single_element_duplicate(self):
        elem = np.array([lambda x: x, "A", "B", "C", "D"], dtype=object)
        assert _is_duplicate(elem, 1, ["A", "B", "C", "D"]) is True

    def test_single_element_not_duplicate(self):
        elem = np.array([lambda x: x, "A", "B", "C", "D"], dtype=object)
        assert _is_duplicate(elem, 1, ["X", "Y", "Z", "W"]) is False

    def test_multiple_duplicate(self):
        elem = np.array(
            [[lambda x: x, "A", "B", "C", "D"], [lambda x: x, "X", "Y", "Z", "W"]],
            dtype=object,
        )
        assert _is_duplicate(elem, 2, ["A", "B", "C", "D"]) is True

    def test_multiple_not_duplicate(self):
        elem = np.array(
            [[lambda x: x, "A", "B", "C", "D"], [lambda x: x, "X", "Y", "Z", "W"]],
            dtype=object,
        )
        assert _is_duplicate(elem, 2, ["New", "Entry", "Here", "!"]) is False


class TestAssignPddx:
    def test_assigns_function(self, sim_opt_with_mocks):
        assign_pddx(lambda: 42.0, ["O", "P", "Ph", "U"], sim_opt_with_mocks, element="fobj")
        assert sim_opt_with_mocks.n_f == 1

    def test_deduplication(self, sim_opt_with_mocks):
        desc = ["S1", "Temperature", "Mix", "K"]
        assign_pddx(lambda: 300.0, desc, sim_opt_with_mocks, element="fobj")
        n_before = sim_opt_with_mocks.n_f
        assign_pddx(lambda: 350.0, desc, sim_opt_with_mocks, element="fobj")
        assert sim_opt_with_mocks.n_f == n_before

    def test_invalid_element_raises(self, sim_opt_with_mocks):
        with pytest.raises(ValueError, match="Unknown element type"):
            assign_pddx(lambda: 1.0, ["A", "B", "C", "D"], sim_opt_with_mocks, element="banana")
