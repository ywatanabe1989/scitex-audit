# scitex-audit

<!-- scitex-badges:start -->
[![PyPI](https://img.shields.io/pypi/v/scitex-audit.svg)](https://pypi.org/project/scitex-audit/)
[![Python](https://img.shields.io/pypi/pyversions/scitex-audit.svg)](https://pypi.org/project/scitex-audit/)
[![Tests](https://github.com/ywatanabe1989/scitex-audit/actions/workflows/test.yml/badge.svg)](https://github.com/ywatanabe1989/scitex-audit/actions/workflows/test.yml)
[![Install Test](https://github.com/ywatanabe1989/scitex-audit/actions/workflows/install-test.yml/badge.svg)](https://github.com/ywatanabe1989/scitex-audit/actions/workflows/install-test.yml)
[![Coverage](https://codecov.io/gh/ywatanabe1989/scitex-audit/graph/badge.svg)](https://codecov.io/gh/ywatanabe1989/scitex-audit)
[![Docs](https://readthedocs.org/projects/scitex-audit/badge/?version=latest)](https://scitex-audit.readthedocs.io/en/latest/)
[![License: AGPL v3](https://img.shields.io/badge/license-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
<!-- scitex-badges:end -->


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
