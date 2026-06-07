#!/usr/bin/env python3
# File: src/scitex_audit/cli.py

"""
scitex-audit CLI — noun-verb command surface.

Subcommands:

* ``scitex-audit github`` — GitHub security-alerts checker (Dependabot
  + secret scanning + code scanning). Absorbed from scitex-security
  0.1.x per ADR-0001 (scitex-dev #139). The legacy ``scitex-security``
  console script in the absorbed shim package is a hard-error redirect
  per CLI-deprecation skill 11 §5 — use ``scitex-audit github`` going
  forward.

The orchestrator ``audit(.)`` API is still importable via Python
(``from scitex_audit import audit``) and is the right entry point for
multi-tool scans; the CLI exists primarily to surface the focused
GitHub-alerts use case the absorbed package previously owned.
"""

from __future__ import annotations

from typing import Optional

import click

from .github import (
    GitHubSecurityError,
    check_github_alerts,
    format_alerts_report,
    save_alerts_to_file,
)


@click.group(name="scitex-audit")
@click.version_option(package_name="scitex-audit", prog_name="scitex-audit")
def main() -> None:
    """SciTeX security-audit toolkit (bandit / shellcheck / pip-audit / github)."""


@main.command("github")
@click.option(
    "--repo",
    "repo",
    default=None,
    help=(
        "GitHub repository in OWNER/NAME form. When omitted, the current "
        "directory's `gh` remote is used."
    ),
)
@click.option(
    "--save/--no-save",
    "save",
    default=False,
    show_default=True,
    help=(
        "Persist the rendered report to "
        "$SCITEX_AUDIT_DIR (or the project/user-scope default) as a "
        "timestamped security-YYYYmmdd_HHMMSS.txt + security-latest.txt "
        "symlink."
    ),
)
def github_cmd(repo: Optional[str], save: bool) -> None:
    """Fetch Dependabot + secret-scanning + code-scanning alerts via gh."""
    try:
        alerts = check_github_alerts(repo)
    except GitHubSecurityError as exc:
        raise click.ClickException(str(exc))

    report = format_alerts_report(alerts)
    click.echo(report)

    if save:
        path = save_alerts_to_file(alerts)
        click.echo(f"\n[scitex-audit] saved → {path}", err=True)


if __name__ == "__main__":  # pragma: no cover
    main()


# EOF
