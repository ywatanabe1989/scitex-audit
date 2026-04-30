#!/usr/bin/env python3
"""Quickstart for scitex-audit: run a Python security audit on a tiny snippet."""

import tempfile
from pathlib import Path

import scitex_audit
from scitex_audit import audit


def main() -> int:
    print(f"scitex_audit.__all__: {scitex_audit.__all__}")

    with tempfile.TemporaryDirectory() as tmp:
        sample = Path(tmp) / "sample.py"
        sample.write_text("import os\nprint('hello')\n")

        # Run only the python check (bandit). Other checks may need extra
        # external binaries (shellcheck, pip-audit, gh) we don't want to require.
        results = audit(str(tmp), checks=["python"])

    print(f"checks executed: {list(results.keys())}")
    py = results.get("python", {})
    print(f"python.status:  {py.get('status')}")
    print(f"python.summary: {py.get('summary')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
