# Quick Start

Run every available checker against the current directory:

```python
from scitex_audit import audit

results = audit(".")
for name, payload in results.items():
    print(name, payload.get("status"), payload.get("summary"))
```

Run a subset:

```python
results = audit(".", checks=["python", "shell"])
```

Write JSON report alongside the in-memory dict:

```python
results = audit(".", output_file="security_report.json")
```

## Return value shape

Per-check keys; each value is a dict with `status` and a human `summary`:

| status       | meaning                                        |
|--------------|------------------------------------------------|
| `ok`         | checker ran, no findings                       |
| `findings`   | checker ran, issues reported                   |
| `skipped`    | backend tool not installed / not authenticated |
| `error`      | checker crashed — see `error` field            |

See [02_python-api.md](02_python-api.md) for the full schema and
[03_checkers.md](03_checkers.md) for backend-specific details.
