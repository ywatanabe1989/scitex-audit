# scitex-audit

Unified security scanning for Python projects. Orchestrates
[bandit](https://bandit.readthedocs.io/) (Python source),
[shellcheck](https://www.shellcheck.net/) (shell scripts),
[pip-audit](https://pypi.org/project/pip-audit/) (dependency vulnerabilities),
and GitHub security alerts into a single report.

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
