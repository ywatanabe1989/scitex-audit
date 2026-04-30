---
name: cli-reference
description: CLI Reference — see file body for details.
tags: [scitex-audit, scitex-package]
---

# CLI Reference

`scitex-audit` does not ship its own console-script entry point. The CLI
surface is exposed as the `audit` subcommand of the umbrella `scitex`
CLI (see the `scitex` package) which dispatches into
`scitex_audit.audit`.

## Usage

```bash
scitex audit .                       # all available checks
scitex audit . --checks python shell # subset
scitex audit . --output report.json  # write JSON
```

Flags mirror the Python API one-to-one:

| Flag          | Maps to Python kwarg |
|---------------|----------------------|
| positional    | `path`               |
| `--checks`    | `checks`             |
| `--output`    | `output_file`        |

Exit code is non-zero only on hard errors (checker crashes); `findings`
alone do not fail the process — inspect the JSON/dict instead.
