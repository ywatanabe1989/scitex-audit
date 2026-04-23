# Python API

The package exposes exactly one public symbol:

```python
from scitex_audit import audit
```

## Signature

```python
audit(
    path: str | Path = ".",
    checks: list[str] | None = None,    # default: all ALL_CHECKS
    output_file: str | Path | None = None,
) -> dict[str, dict]
```

* `path` — root directory to scan. Bandit and shellcheck recurse into it.
* `checks` — iterable of check names. Any subset of
  `("python", "shell", "deps", "github")`. `None` runs all.
* `output_file` — optional JSON path; same dict is still returned.

## Result dict

Keys mirror `checks`. Each value is a dict with at minimum:

* `status`: one of `ok`, `findings`, `skipped`, `error`
* `summary`: short human string
* `findings`: list of finding dicts (present when status is `findings`)
* `tool`: backend name (e.g. `bandit`, `shellcheck`, `pip-audit`, `gh`)
* `error`: present only when `status == "error"`

## Availability gating

If the underlying CLI is missing from `PATH`, that checker reports
`status="skipped"` instead of failing. `github` additionally requires `gh
auth status` to succeed.

## Constants

`scitex_audit._runner.ALL_CHECKS == ("python", "shell", "deps", "github")`.
