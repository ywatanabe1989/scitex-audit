#!/usr/bin/env python3
# File: src/scitex_audit/cli.py

"""
scitex-audit CLI — noun-verb command surface.

Subcommands:

* ``scitex-audit github check`` — GitHub security-alerts checker
  (Dependabot + secret scanning + code scanning). Absorbed from
  scitex-security 0.1.x per ADR-0001 (scitex-dev #139). The legacy
  ``scitex-security`` console script in the absorbed shim package is
  a hard-error redirect per CLI-deprecation skill 11 §5 — use
  ``scitex-audit github check`` (or ``scitex-audit github show-latest``)
  going forward.
* ``scitex-audit github show-latest`` — print the most recent saved
  alerts report.

The orchestrator ``audit(.)`` API is still importable via Python
(``from scitex_audit import audit``) and is the right entry point for
multi-tool scans; the CLI exists primarily to surface the focused
GitHub-alerts use case the absorbed package previously owned.
"""

from __future__ import annotations

import json as _json
from pathlib import Path
from typing import Optional

import click

from .github import (
    GitHubSecurityError,
    check_github_alerts,
    format_alerts_report,
    get_latest_alerts_file,
    save_alerts_to_file,
)


def _version() -> str:
    try:
        from importlib.metadata import version

        return version("scitex-audit")
    except Exception:  # pragma: no cover
        return "unknown"


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(_version(), "-V", "--version", prog_name="scitex-audit")
@click.help_option("-h", "--help")
@click.option("--help-recursive", is_flag=True, help="Show help for all subcommands.")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Emit structured JSON output (propagates to subcommands that honour it).",
)
@click.pass_context
def main(ctx: click.Context, help_recursive: bool, as_json: bool) -> None:
    """scitex-audit — security audit toolkit (bandit / shellcheck / pip-audit / github).

    \b
    Config is loaded with the SciTeX precedence chain:
      config.yaml -> $SCITEX_AUDIT_CONFIG -> ~/.scitex/audit/config.yaml -> defaults

    \b
    Storage:
      Alert reports default to $SCITEX_AUDIT_DIR (or project-scope
      <git-root>/.scitex/audit/github-alerts/, or user-scope
      ~/.scitex/audit/github-alerts/).
    """
    ctx.ensure_object(dict)
    ctx.obj["as_json"] = as_json
    if help_recursive:
        _show_recursive_help(ctx)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


def _show_recursive_help(ctx: click.Context) -> None:
    """Print help for the root group plus every subcommand recursively."""
    click.echo(ctx.get_help())
    click.echo()
    group = ctx.command
    if isinstance(group, click.Group):
        for name in sorted(group.list_commands(ctx)):
            cmd = group.get_command(ctx, name)
            if cmd is None or cmd.hidden:
                continue
            sub_ctx = click.Context(cmd, parent=ctx, info_name=name)
            click.echo("=" * 60)
            click.echo(f"Command: {name}")
            click.echo("=" * 60)
            click.echo(sub_ctx.get_help())
            click.echo()
            if isinstance(cmd, click.Group):
                for sub_name in sorted(cmd.list_commands(sub_ctx)):
                    sub_cmd = cmd.get_command(sub_ctx, sub_name)
                    if sub_cmd is None or sub_cmd.hidden:
                        continue
                    sub_sub_ctx = click.Context(
                        sub_cmd, parent=sub_ctx, info_name=sub_name
                    )
                    click.echo("-" * 60)
                    click.echo(f"Command: {name} {sub_name}")
                    click.echo("-" * 60)
                    click.echo(sub_sub_ctx.get_help())
                    click.echo()


# --------------------------------------------------------------------------- #
# `scitex-audit github` — noun subgroup, verb children                        #
# --------------------------------------------------------------------------- #


@main.group(name="github", invoke_without_command=True)
@click.pass_context
def github_group(ctx: click.Context) -> None:
    """GitHub security-alerts commands (Dependabot / CodeQL / secret scanning).

    \b
    Example:
      $ scitex-audit github check .
      $ scitex-audit github show-latest
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@github_group.command("check")
@click.argument("repo", required=False, default=".")
@click.option(
    "--save",
    is_flag=True,
    help=(
        "Persist the rendered report to "
        "$SCITEX_AUDIT_DIR (or the project/user-scope default) as a "
        "timestamped security-YYYYmmdd_HHMMSS.txt + security-latest.txt "
        "symlink."
    ),
)
@click.option(
    "--output-dir",
    default=None,
    help="Output directory for --save (default: ~/.scitex/audit/github-alerts/).",
)
@click.option("--json", "as_json", is_flag=True, help="Emit JSON instead of text.")
@click.pass_context
def github_check(
    ctx: click.Context,
    repo: str,
    save: bool,
    output_dir: Optional[str],
    as_json: bool,
) -> None:
    """Check Dependabot / CodeQL / secret-scanning alerts for REPO.

    REPO is 'owner/repo'. Use '.' (default) to auto-detect from the current
    git repo.

    \b
    Example:
      $ scitex-audit github check .
      $ scitex-audit github check ywatanabe1989/scitex-audit
      $ scitex-audit github check . --save
      $ scitex-audit github check . --json
    """
    as_json = as_json or bool(ctx.obj.get("as_json"))
    try:
        alerts = check_github_alerts(None if repo == "." else repo)

        total = sum(
            len([a for a in alerts[key] if a.get("state") == "open"]) for key in alerts
        )

        saved_path = None
        if save:
            out_path = Path(output_dir) if output_dir else None
            saved_path = save_alerts_to_file(alerts, out_path)

        if as_json:
            payload = {
                "repo": repo,
                "open_alerts": total,
                "alerts": alerts,
                "saved_path": str(saved_path) if saved_path else None,
            }
            click.echo(_json.dumps(payload, indent=2, default=str))
        else:
            if saved_path:
                click.echo(f"Report saved to: {saved_path}")
                click.echo(
                    f"Latest symlink: {saved_path.parent / 'security-latest.txt'}"
                )
            click.echo(format_alerts_report(alerts))
            if total > 0:
                click.echo(f"Found {total} open security alert(s)", err=True)

        ctx.exit(1 if total > 0 else 0)

    except GitHubSecurityError as e:
        if as_json:
            click.echo(_json.dumps({"error": str(e)}, indent=2), err=True)
        else:
            click.echo(f"ERROR: {e}", err=True)
        ctx.exit(2)


@github_group.command("show-latest")
@click.option(
    "--alerts-dir",
    default=None,
    help="Directory holding saved reports (default: ~/.scitex/audit/github-alerts/).",
)
@click.option("--json", "as_json", is_flag=True, help="Emit JSON instead of text.")
@click.pass_context
def github_show_latest(
    ctx: click.Context, alerts_dir: Optional[str], as_json: bool
) -> None:
    """Print the most recent saved alerts report.

    \b
    Example:
      $ scitex-audit github show-latest
      $ scitex-audit github show-latest --alerts-dir ~/.scitex/audit/github-alerts
      $ scitex-audit github show-latest --json
    """
    as_json = as_json or bool(ctx.obj.get("as_json"))
    dir_path = Path(alerts_dir) if alerts_dir else None

    try:
        latest_file = get_latest_alerts_file(dir_path)
    except Exception as e:
        if as_json:
            click.echo(_json.dumps({"error": str(e)}, indent=2), err=True)
        else:
            click.echo(f"ERROR: {e}", err=True)
        ctx.exit(2)
        return

    if not latest_file:
        if as_json:
            click.echo(_json.dumps({"latest": None}, indent=2))
        else:
            click.echo("No alerts files found", err=True)
        ctx.exit(1)
        return

    try:
        content = latest_file.read_text()
    except Exception as e:
        if as_json:
            click.echo(_json.dumps({"error": str(e)}, indent=2), err=True)
        else:
            click.echo(f"ERROR: {e}", err=True)
        ctx.exit(2)
        return

    if as_json:
        click.echo(
            _json.dumps({"latest": str(latest_file), "content": content}, indent=2)
        )
    else:
        click.echo(content)


# --------------------------------------------------------------------------- #
# Introspection / housekeeping commands required by the audit-cli conformance #
# --------------------------------------------------------------------------- #


@main.command("list-python-apis")
@click.option("-v", "--verbose", count=True, help="-v names, -vv +sigs, -vvv +docs")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
@click.pass_context
def list_python_apis(ctx: click.Context, verbose: int, as_json: bool) -> None:
    """List public Python APIs in scitex-audit.

    \b
    Example:
      $ scitex-audit list-python-apis
      $ scitex-audit list-python-apis -vv
      $ scitex-audit list-python-apis --json
    """
    import inspect

    import scitex_audit

    as_json = as_json or bool(ctx.obj.get("as_json"))

    names = sorted(getattr(scitex_audit, "__all__", []))
    apis = []
    for name in names:
        obj = getattr(scitex_audit, name, None)
        if obj is None:
            continue
        entry = {"name": name, "type": type(obj).__name__}
        if callable(obj):
            try:
                entry["signature"] = str(inspect.signature(obj))
            except (TypeError, ValueError):
                pass
        doc = inspect.getdoc(obj) or ""
        if doc:
            entry["doc"] = doc.strip().split("\n")[0]
        apis.append(entry)

    if as_json:
        click.echo(_json.dumps({"module": "scitex_audit", "apis": apis}, indent=2))
        return

    click.secho("scitex_audit Python APIs", fg="cyan", bold=True)
    for api in apis:
        sig = api.get("signature", "")
        click.echo(f"  {click.style(api['name'], fg='green')}{sig}")
        if verbose >= 2 and api.get("doc"):
            click.echo(f"    {api['doc']}")


@main.group(invoke_without_command=True)
@click.pass_context
def mcp(ctx: click.Context) -> None:
    """MCP (Model Context Protocol) commands. scitex-audit ships no MCP server."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@mcp.command("list-tools")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
@click.pass_context
def mcp_list_tools(ctx: click.Context, as_json: bool) -> None:
    """List MCP tools exposed by scitex-audit (currently none).

    \b
    Example:
      $ scitex-audit mcp list-tools
      $ scitex-audit mcp list-tools --json
    """
    as_json = as_json or bool(ctx.obj.get("as_json"))
    if as_json:
        click.echo(_json.dumps({"total": 0, "tools": []}, indent=2))
        return
    click.secho("scitex-audit MCP: 0 tools (no MCP server)", fg="cyan", bold=True)


# Wire the skills group (audit-cli §1a — packages with _skills/ MUST
# expose `<cli> skills {list,get,install}`).
from ._skills import skills_group as _skills_group

main.add_command(_skills_group, name="skills")


# Wire canonical install-shell-completion + print-shell-completion (§1a).
# scitex-dev is an optional/dev dep at the CLI layer; if it's not present
# (e.g. user installed scitex-audit alone) the completion commands aren't
# wired — the audit-cli gate runs in CI environments where scitex-dev is
# always present.
try:
    from scitex_dev._cli._completion import attach_shell_completion

    attach_shell_completion(main, prog_name="scitex-audit")
except ImportError:
    pass


# audit §4 — inject version into root --help
try:
    from importlib.metadata import version as _v

    main.help = (
        f"scitex-audit (v{_v('scitex-audit')}) — " + (main.help or "").lstrip()
    )
except Exception:
    pass


if __name__ == "__main__":  # pragma: no cover
    main()


# EOF
