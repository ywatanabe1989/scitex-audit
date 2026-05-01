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

<p align="center">
  <a href="https://scitex.ai">
    <img src="docs/scitex-logo-blue-cropped.png" alt="SciTeX" width="400">
  </a>
</p>

<p align="center"><b>Unified security scanning: bandit + shellcheck + pip-audit + GitHub advisories in one report.</b></p>

<p align="center">
  <a href="https://scitex-audit.readthedocs.io/">Full Documentation</a> · <code>pip install scitex-audit</code>
</p>

---

## Problem and Solution

| # | Problem | Solution |
|---|---------|----------|
| 1 | **Security scanning requires 4 tools run separately** — `bandit` (py) + `shellcheck` (sh) + `pip-audit` (deps) + GH Advisories — each with different output format | **`scitex-audit .`** — runs all four, merges findings into one JSON report; ideal for CI pre-release gates |

## Installation

```bash
pip install scitex-audit
# With all scanner backends:
pip install scitex-audit[all]
```

## Quick Start

```python
from scitex_audit import audit

results = audit(".")
results = audit(".", checks=["python", "shell"])
```

## 2 Interfaces

<details>
<summary><strong>Python API</strong></summary>

<br>

```python
from scitex_audit import audit

# Run all enabled scanners and merge results.
results = audit(".")

# Run only specific scanners.
results = audit(".", checks=["python", "shell"])
```

</details>

<details>
<summary><strong>CLI</strong></summary>

<br>

```bash
scitex-audit .                          # all scanners
scitex-audit . --checks python,shell    # subset
scitex-audit . --json                   # machine-readable
```

</details>

## Part of SciTeX

`scitex-audit` is part of [**SciTeX**](https://scitex.ai). Install via
the umbrella with `pip install scitex[audit]` to use as
`scitex.audit` (Python) or `scitex audit ...` (CLI).

>Four Freedoms for Research
>
>0. The freedom to **run** your research anywhere — your machine, your terms.
>1. The freedom to **study** how every step works — from raw data to final manuscript.
>2. The freedom to **redistribute** your workflows, not just your papers.
>3. The freedom to **modify** any module and share improvements with the community.
>
>AGPL-3.0 — because we believe research infrastructure deserves the same freedoms as the software it runs on.

## License

AGPL-3.0 — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <a href="https://scitex.ai" target="_blank"><img src="docs/scitex-icon-navy-inverted.png" alt="SciTeX" width="40"/></a>
</p>
