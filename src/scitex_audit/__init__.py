#!/usr/bin/env python3
# File: src/scitex_audit/__init__.py

"""
SciTeX Audit Module

Unified security scanning by orchestrating bandit (Python), shellcheck (shell),
pip-audit (deps), and GitHub alerts.

Usage:
    from scitex_audit import audit

    results = audit(".")
    results = audit(".", checks=["python", "shell"])
"""

from __future__ import annotations

try:
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as _v

    try:
        __version__ = _v("scitex-audit")
    except PackageNotFoundError:
        __version__ = "0.0.0+local"
    del _v, PackageNotFoundError
except ImportError:  # pragma: no cover — only on ancient Pythons
    __version__ = "0.0.0+local"

from ._runner import audit

__all__ = ["__version__", "audit"]

# EOF
