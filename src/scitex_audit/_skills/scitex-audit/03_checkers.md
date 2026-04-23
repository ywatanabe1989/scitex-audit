# Checker Backends

Four independent checkers; each maps to one external tool.

| Name     | Tool        | Requirement               |
|----------|-------------|---------------------------|
| `python` | `bandit`    | `bandit` on PATH          |
| `shell`  | `shellcheck`| `shellcheck` on PATH      |
| `deps`   | `pip-audit` | `pip-audit` on PATH       |
| `github` | `gh`        | `gh` on PATH + authenticated |

## python — bandit

Static analysis of `.py` files. Reports per-issue severity, CWE, line
number. Low-noise default configuration (no custom `.bandit` file
required).

## shell — shellcheck

Lints `.sh` / `.bash` scripts. Reports rule code, message, and line.

## deps — pip-audit

Scans the current Python environment (or `requirements.txt` if picked up
by pip-audit) for known CVEs in installed packages.

## github — GitHub security alerts

Calls `gh api /repos/{owner}/{repo}/vulnerability-alerts` via the
authenticated `gh` CLI. Silently skips if `gh auth status` fails.

## Individual runner functions

Internal helpers (not part of the public API, but useful when embedding):

* `scitex_audit._bandit.run_bandit(path)`
* `scitex_audit._shellcheck.run_shellcheck(path)`
* `scitex_audit._pip_audit.run_pip_audit(path)`
* `scitex_audit._github.run_github_check(path)`

Prefer `audit()` in user code — it handles tool-availability gating and
result normalization.
