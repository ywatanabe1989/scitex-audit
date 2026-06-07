"""Entry point for `python -m scitex_audit`."""

from scitex_audit.cli import main


if __name__ == "__main__":
    raise SystemExit(main() or 0)


# EOF
