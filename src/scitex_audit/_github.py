#!/usr/bin/env python3
# File: src/scitex_audit/_github.py

"""
GitHub security alerts checker.

Uses gh CLI directly instead of depending on scitex.security.
Falls back gracefully if scitex.security is available.
"""

from __future__ import annotations

import json
import logging
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)


class GitHubSecurityError(Exception):
    """Error fetching GitHub security data."""


def _get_current_repo() -> Optional[str]:
    """Detect the current GitHub repository from git remote."""
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


def _fetch_alerts(repo: str, alert_type: str) -> list[dict]:
    """Fetch alerts of a given type from GitHub API."""
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{repo}/{alert_type}", "--paginate"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            if isinstance(data, list):
                return data
    except Exception as exc:
        logger.debug("Failed to fetch %s alerts: %s", alert_type, exc)
    return []


def run_github_check(repo: Optional[str] = None) -> dict:
    """Fetch GitHub security alerts and return normalized results.

    Parameters
    ----------
    repo : str | None
        Repository in "owner/repo" format. None uses the current repo.

    Returns
    -------
    dict
        {status, findings, summary} in the standard audit format.
    """
    if repo is None:
        repo = _get_current_repo()
        if repo is None:
            return {
                "status": "error",
                "findings": [],
                "summary": "Could not determine current repository",
            }

    # Try to use scitex.security if available (optional dependency)
    try:
        from scitex.security import GitHubSecurityError as _GSE
        from scitex.security import check_github_alerts

        try:
            alerts = check_github_alerts(repo)
        except _GSE as exc:
            return {"status": "error", "findings": [], "summary": str(exc)}

        total = sum(len(v) for v in alerts.values())
        findings = []
        for category, items in alerts.items():
            for item in items:
                findings.append({"category": category, **item})

        if total == 0:
            return {"status": "ok", "findings": [], "summary": "No open alerts"}

        parts = [f"{len(alerts[k])} {k}" for k in alerts if alerts[k]]
        summary = f"{total} alerts ({', '.join(parts)})"

        return {"status": "findings", "findings": findings, "summary": summary}

    except ImportError:
        # Standalone mode: use gh CLI directly
        alert_types = {
            "dependabot": "dependabot/alerts?state=open",
            "code-scanning": "code-scanning/alerts?state=open",
            "secret-scanning": "secret-scanning/alerts?state=open",
        }

        findings = []
        for category, endpoint in alert_types.items():
            alerts = _fetch_alerts(repo, endpoint)
            for alert in alerts:
                findings.append({
                    "category": category,
                    "summary": alert.get("security_advisory", {}).get("summary", "")
                    or alert.get("rule", {}).get("description", "")
                    or alert.get("secret_type_display_name", ""),
                    "severity": alert.get("security_advisory", {}).get("severity", "")
                    or alert.get("rule", {}).get("severity", ""),
                    "url": alert.get("html_url", ""),
                })

        if not findings:
            return {"status": "ok", "findings": [], "summary": "No open alerts"}

        summary = f"{len(findings)} alerts"
        return {"status": "findings", "findings": findings, "summary": summary}


# EOF
