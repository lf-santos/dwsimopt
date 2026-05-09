"""Pytest configuration and shared fixtures."""

import os

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "requires_dwsim: marks tests that need DWSIM installed"
    )


def pytest_collection_modifyitems(config, items):
    """Skip DWSIM tests if DWSIM is not available."""
    dwsim_available = any(
        "DWSIM" in entry.upper()
        for entry in os.environ.get("PATH", "").split(os.pathsep)
    )
    if not dwsim_available:
        skip_marker = pytest.mark.skip(reason="DWSIM not found in PATH")
        for item in items:
            if "requires_dwsim" in item.keywords:
                item.add_marker(skip_marker)
