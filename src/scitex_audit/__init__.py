#!/usr/bin/env python3
# File: src/scitex_audit/__init__.py

"""
SciTeX Audit Module

Unified security scanning by orchestrating bandit (Python), shellcheck (shell),
pip-audit (deps), and GitHub alerts.

Usage:
    from scitex_audit import audit, check_github_alerts

    results = audit(".")
    results = audit(".", checks=["python", "shell"])

    # GitHub alerts directly (absorbed from scitex-security per ADR-0001):
    alerts = check_github_alerts()
"""

from __future__ import annotations

import logging as _logging

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
from .github import (
    GitHubSecurityError,
    check_github_alerts,
    format_alerts_report,
    get_latest_alerts_file,
    save_alerts_to_file,
)

# One-shot migration of legacy ~/.scitex/security/ → ~/.scitex/audit/
# from the absorbed scitex-security 0.1.x package. Guarded by a marker
# file inside _paths so it only fires once per user. Wrapped in
# try/except — a path-migration glitch must never break import. See
# ADR-0001 (scitex-dev #139) §"Locked decisions" #2.
try:
    from ._paths import _migrate_legacy_security_dir as _migrate

    _migrate()
    del _migrate
except Exception:  # pragma: no cover — best-effort migration
    _logging.getLogger(__name__).debug(
        "scitex-audit: legacy ~/.scitex/security/ migration probe raised; "
        "continuing.",
        exc_info=True,
    )

__all__ = [
    "__version__",
    "audit",
    # Absorbed scitex-security public surface (5 symbols per ADR-0001):
    "GitHubSecurityError",
    "check_github_alerts",
    "format_alerts_report",
    "get_latest_alerts_file",
    "save_alerts_to_file",
]

# EOF
