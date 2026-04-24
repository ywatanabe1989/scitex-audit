# scitex-audit

Unified security scanning for Python projects. Orchestrates
[bandit](https://bandit.readthedocs.io/) (Python source),
[shellcheck](https://www.shellcheck.net/) (shell scripts),
[pip-audit](https://pypi.org/project/pip-audit/) (dependency vulnerabilities),
and GitHub security alerts into a single report.

> **Interfaces:** Python ⭐ · CLI ⭐⭐⭐ (primary) · MCP ⭐ · Skills ⭐ · Hook — · HTTP —

## Problem and Solution


| # | Problem | Solution |
|---|---------|----------|
| 1 | **Security scanning requires 4 tools run separately** -- `bandit` (py) + `shellcheck` (sh) + `pip-audit` (deps) + GH Advisories — each with different output format | **`scitex audit .`** -- runs all four, merges findings into one JSON report; ideal for CI pre-release gates |

## Installation

```bash
pip install scitex-audit
# With all scanner backends:
pip install scitex-audit[all]
```

## Usage

```python
from scitex_audit import audit

results = audit(".")
results = audit(".", checks=["python", "shell"])
```

## License

AGPL-3.0 -- see [LICENSE](LICENSE) for details.
