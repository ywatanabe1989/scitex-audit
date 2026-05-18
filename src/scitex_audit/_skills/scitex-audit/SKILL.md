---
name: scitex-audit
description: |
  [WHAT] Unified repo security scanner for scientific Python projects — one call orchestrates `bandit` (Python AST security linter), `shellcheck` (shell-script linter), `pip-audit` (Python dependency CVE scanner), and GitHub Security Advisory alerts, merging their findings into a single JSON report. Public API (1 symbol) — `audit(path: str = ".", checks: Optional[list[str]] = None, output_file…
  [WHEN] Use whenever the user asks to "audit this repo for security issues", "run bandit on this project", "check Python deps for CVEs with pip-audit", "lint shell scripts with shellcheck", "merge security scan results into one report", "pull GitHub security advisories", or mentions `scitex audit`, `scitex.
  [HOW] audit`, unified security scan.
tags: [scitex-audit]
primary_interface: cli
interfaces:
  python: 1
  cli: 3
  mcp: 1
  skills: 1
  http: 0
---

# scitex-audit

> **Interfaces:** Python ⭐ · CLI ⭐⭐⭐ (primary) · MCP ⭐ · Skills ⭐ · Hook — · HTTP —

Single-entry security scanner. One `audit()` call dispatches across the
installed checker backends and merges their findings.

## Installation & import (two equivalent paths)

The same module is reachable via two install paths. Both forms work at
runtime; which one a user has depends on their install choice.

```python
# Standalone — pip install scitex-audit
import scitex_audit
scitex_audit.audit(...)

# Umbrella — pip install scitex
import scitex.audit
scitex.audit.audit(...)
```

`pip install scitex-audit` alone does NOT expose the `scitex` namespace;
`import scitex.audit` raises `ModuleNotFoundError`. To use the
`scitex.audit` form, also `pip install scitex`.

See [../../general/02_interface-python-api.md] for the ecosystem-wide
rule and empirical verification table.

## Sub-skills

### Core

* [01_installation](01_installation.md) — pip install + optional backends + verify
* [02_quick-start](02_quick-start.md) — Minimal usage, all checks / subset
* [03_python-api](03_python-api.md) — `audit()` signature and result schema

### Interface

* [10_cli-reference](10_cli-reference.md) — `scitex audit` subcommand (via parent CLI)
* [11_checkers](11_checkers.md) — The four checker backends
