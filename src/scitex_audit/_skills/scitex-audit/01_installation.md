---
description: |
  [TOPIC] Installation
  [DETAILS] pip install scitex-audit. Optional system tools (`bandit`, `shellcheck`, `pip-audit`, `gh`) extend coverage but are auto-skipped when missing.
tags: [scitex-audit-installation]
---

# Installation

## Standard

```bash
pip install scitex-audit
```

Pure-Python; no required system deps. Each checker auto-skips if its backend
binary isn't installed (status `skipped` in the merged report).

## Optional backends

| Backend     | Install                                  | Covers                          |
|-------------|------------------------------------------|---------------------------------|
| `bandit`    | `pip install bandit`                     | Python AST security lint        |
| `pip-audit` | `pip install pip-audit`                  | Python dependency CVEs          |
| `shellcheck`| `apt install shellcheck` / `brew install shellcheck` | Shell-script lint  |
| `gh`        | https://cli.github.com/                  | GitHub Security Advisory alerts |

## Verify

```bash
python -c "import scitex_audit; print(scitex_audit.__version__)"
python -c "from scitex_audit import audit; print(audit('.', checks=[]))"
```

## Editable install (development)

```bash
git clone https://github.com/ywatanabe1989/scitex-audit
cd scitex-audit
pip install -e .
```
