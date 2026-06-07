#!/usr/bin/env python3
"""Tests for the scitex-security → scitex-audit absorption (ADR-0001 W1).

Covers the public surface that scitex-security 0.1.x consumers
relied on, now re-homed in ``scitex_audit.github``. These are
import + signature assertions; behavioural tests for the underlying
gh-CLI plumbing live in scitex-security 0.1.4's own test suite (the
implementation was ported verbatim).

PA-307 test-quality: every test carries the canonical
``# Arrange`` / ``# Act`` / ``# Assert`` markers each on its own line.
PA-306 no-mocks: no patching; we exercise the real module surface.
"""

from __future__ import annotations


def test_github_module_exposes_check_github_alerts():
    """``scitex_audit.github.check_github_alerts`` is importable."""
    # Arrange
    import scitex_audit.github as gh

    # Act
    has_attr = hasattr(gh, "check_github_alerts")
    # Assert
    assert has_attr


def test_github_module_exposes_save_alerts_to_file():
    """``scitex_audit.github.save_alerts_to_file`` is importable."""
    # Arrange
    import scitex_audit.github as gh

    # Act
    has_attr = hasattr(gh, "save_alerts_to_file")
    # Assert
    assert has_attr


def test_github_module_exposes_get_latest_alerts_file():
    """``scitex_audit.github.get_latest_alerts_file`` is importable."""
    # Arrange
    import scitex_audit.github as gh

    # Act
    has_attr = hasattr(gh, "get_latest_alerts_file")
    # Assert
    assert has_attr


def test_github_module_exposes_format_alerts_report():
    """``scitex_audit.github.format_alerts_report`` is importable."""
    # Arrange
    import scitex_audit.github as gh

    # Act
    has_attr = hasattr(gh, "format_alerts_report")
    # Assert
    assert has_attr


def test_github_module_exposes_github_security_error():
    """``scitex_audit.github.GitHubSecurityError`` is importable."""
    # Arrange
    import scitex_audit.github as gh

    # Act
    has_attr = hasattr(gh, "GitHubSecurityError")
    # Assert
    assert has_attr


def test_package_root_reexports_check_github_alerts():
    """``scitex_audit.check_github_alerts`` is in the package `__all__`."""
    # Arrange
    import scitex_audit

    # Act
    in_all = "check_github_alerts" in scitex_audit.__all__
    # Assert
    assert in_all


def test_package_root_reexports_save_alerts_to_file():
    """``scitex_audit.save_alerts_to_file`` is in the package `__all__`."""
    # Arrange
    import scitex_audit

    # Act
    in_all = "save_alerts_to_file" in scitex_audit.__all__
    # Assert
    assert in_all


def test_package_root_reexports_get_latest_alerts_file():
    """``scitex_audit.get_latest_alerts_file`` is in the package `__all__`."""
    # Arrange
    import scitex_audit

    # Act
    in_all = "get_latest_alerts_file" in scitex_audit.__all__
    # Assert
    assert in_all


def test_package_root_reexports_format_alerts_report():
    """``scitex_audit.format_alerts_report`` is in the package `__all__`."""
    # Arrange
    import scitex_audit

    # Act
    in_all = "format_alerts_report" in scitex_audit.__all__
    # Assert
    assert in_all


def test_package_root_reexports_github_security_error():
    """``scitex_audit.GitHubSecurityError`` is in the package `__all__`."""
    # Arrange
    import scitex_audit

    # Act
    in_all = "GitHubSecurityError" in scitex_audit.__all__
    # Assert
    assert in_all


def test_runner_github_check_no_longer_imports_scitex_security():
    """`scitex_audit._github` has no real `scitex_security` import.

    ADR-0001 §"Locked decisions" #4 (no-tombstones, same-wave): the
    ``try: from scitex_security import …`` path was removed in 0.2.0;
    the orchestrator delegates to the native ``scitex_audit.github``.
    Walks the module AST so that prose mentions of "scitex_security"
    in docstrings/comments don't false-positive.
    """
    # Arrange
    import ast
    import inspect

    from scitex_audit import _github

    tree = ast.parse(inspect.getsource(_github))
    imported_modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)
    # Act
    has_legacy_import = any(m.startswith("scitex_security") for m in imported_modules)
    # Assert
    assert not has_legacy_import


def test_paths_default_alerts_dir_is_under_audit_namespace(tmp_path):
    """`_paths.get_default_alerts_dir` returns a path under ``audit/``.

    PA-306 §3 no-mocks: no monkeypatch — we save/restore env + cwd by
    hand so the audit-conformance gate (which rejects fixture-based
    state mutation) stays green.
    """
    # Arrange
    import os

    saved_scitex_dir = os.environ.get("SCITEX_DIR")
    saved_audit_dir = os.environ.get("SCITEX_AUDIT_DIR")
    saved_cwd = os.getcwd()
    os.environ["SCITEX_DIR"] = str(tmp_path)
    os.environ.pop("SCITEX_AUDIT_DIR", None)
    os.chdir(tmp_path)
    try:
        from scitex_audit._paths import get_default_alerts_dir

        # Act
        resolved = get_default_alerts_dir()
        # Assert
        assert "audit" in resolved.parts
    finally:
        os.chdir(saved_cwd)
        if saved_scitex_dir is None:
            os.environ.pop("SCITEX_DIR", None)
        else:
            os.environ["SCITEX_DIR"] = saved_scitex_dir
        if saved_audit_dir is not None:
            os.environ["SCITEX_AUDIT_DIR"] = saved_audit_dir


def test_format_alerts_report_handles_empty_categories():
    """`format_alerts_report` produces a clean 'no alerts' report."""
    # Arrange
    from scitex_audit.github import format_alerts_report

    empty = {"secrets": [], "dependabot": [], "code_scanning": []}
    # Act
    report = format_alerts_report(empty)
    # Assert
    assert "Total open alerts: 0" in report


# EOF
