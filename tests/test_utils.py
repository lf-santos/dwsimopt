"""Tests for the utils module."""

from pathlib import Path

from dwsimopt.utils import PATH2DWSIMOPT


class TestUtils:
    def test_is_path(self):
        assert isinstance(PATH2DWSIMOPT, Path)

    def test_is_absolute(self):
        assert PATH2DWSIMOPT.is_absolute()

    def test_exists(self):
        assert PATH2DWSIMOPT.exists()
