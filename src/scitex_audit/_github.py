#!/usr/bin/env python3
# File: src/scitex_audit/_github.py

"""
GitHub security alerts orchestrator (audit-runner adapter).

Thin adapter that turns the native ``scitex_audit.github.check_github_alerts``
result into the unified ``{status, findings, summary}`` envelope every
audit-runner check returns. Per ADR-0001 (scitex-dev #139, Accepted
2026-06-07), this module no longer imports ``scitex_security`` — that
package was absorbed and the canonical implementation lives in
``scitex_audit.github``.

Repo discovery (``_get_current_repo``) stays here because it's purely
an audit-runner concern (the public ``check_github_alerts`` accepts a
caller-supplied ``repo`` argument).
"""

from __future__ import annotations

import logging
import subprocess
from typing import Optional

# Re-export so any pre-absorption caller of
# ``from scitex_audit._github import GitHubSecurityError`` still works
# without touching the new public submodule.
from .github import GitHubSecurityError, check_github_alerts

logger = logging.getLogger(__name__)


__all__ = ["GitHubSecurityError", "run_github_check"]


def _get_current_repo() -> Optional[str]:
    """Detect the current GitHub repository from the local git remote."""
    try:
        result = subprocess.run(
            ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None


def run_github_check(repo: Optional[str] = None) -> dict:
    """Fetch GitHub security alerts and return the unified audit envelope.

    Parameters
    ----------
    repo : str | None
        Repository in ``"owner/repo"`` format. ``None`` uses the current
        repo (detected from the local ``gh`` remote).

    Returns
    -------
    dict
        ``{status, findings, summary}`` in the standard audit format.

        - ``status="error"`` — repo not detectable, or
          ``GitHubSecurityError`` from the native checker (typically
          unauthenticated ``gh``).
        - ``status="ok"`` — zero open alerts.
        - ``status="findings"`` — one or more open alerts; ``findings``
          is a flat list of ``{category, ...}`` dicts.
    """
    if repo is None:
        repo = _get_current_repo()
        if repo is None:
            return {
                "status": "error",
                "findings": [],
                "summary": "Could not determine current repository",
            }

    try:
        alerts = check_github_alerts(repo)
    except GitHubSecurityError as exc:
        return {"status": "error", "findings": [], "summary": str(exc)}

    total = sum(len(v) for v in alerts.values())
    findings: list[dict] = []
    for category, items in alerts.items():
        for item in items:
            findings.append({"category": category, **item})

    if total == 0:
        return {"status": "ok", "findings": [], "summary": "No open alerts"}

    parts = [f"{len(alerts[k])} {k}" for k in alerts if alerts[k]]
    summary = f"{total} alerts ({', '.join(parts)})"

    return {"status": "findings", "findings": findings, "summary": summary}


# EOF
