"""Path resolution for scitex-audit local state.

Follows the SciTeX local-state-directories convention
(``01_ecosystem/06_local-state-directories.md``):

* Regenerable data (alert reports, symlinks) goes under
  ``<pkg-short>/`` — never outside the package namespace.
* Resolves via ``SCITEX_AUDIT_DIR`` env var, project scope, or user
  scope (in that precedence order).
* ``SCITEX_DIR`` relocates the user-scope root atomically.
* Standalone resolver — no ``scitex_dev`` import, no ``PathManager``
  dependency.

This module also owns the one-time migration of legacy
``~/.scitex/security/`` (from the pre-absorption scitex-security 0.1.x
package) into the new ``~/.scitex/audit/github-alerts/`` layout. The
migration is triggered automatically on package import via
``_migrate_legacy_security_dir`` — no manual user step. See ADR-0001
(scitex-dev #139) for the absorption design.
"""

from __future__ import annotations

import logging
import os
import shutil
import warnings
from pathlib import Path

#: Package short name (``scitex-audit`` → ``audit``).
PKG_SHORT = "audit"

#: GitHub-alerts subdirectory under the package short name. Keeps the
#: github checker output cleanly separated from bandit/shellcheck/pip-
#: audit results that share the same parent.
ALERTS_SUBDIR = "github-alerts"

#: Legacy location (pre-v0.2) — CWD-relative seed scitex-security
#: carried over from its own pre-v0.2 days. Kept here so users
#: migrating straight from a very old scitex-security still get a
#: clean read.
_LEGACY_REL_ALERTS_DIR = Path("logs") / "security"

#: Legacy USER-scope directory from scitex-security 0.1.x.
_LEGACY_USER_SECURITY_SUBDIR = "security"

#: Marker file recording one-shot migrations (per category).
_LEGACY_REL_MARKER = ".migrated_from_legacy"
_LEGACY_SECURITY_USER_MARKER = ".migrated_from_scitex_security_user"

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Scope resolution
# ---------------------------------------------------------------------------


def _project_root() -> Path | None:
    """Walk up from ``cwd`` to find the repository root (``.git`` sentinel)."""
    cwd = Path.cwd().resolve()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".git").is_dir():
            return parent
    return None


def _scitex_dir() -> Path:
    """User-scope SciTeX root (``$SCITEX_DIR`` or ``~/.scitex``)."""
    raw = os.environ.get("SCITEX_DIR", Path.home() / ".scitex")
    return Path(raw).expanduser().resolve()


def _resolve_user_scope() -> Path:
    """User-scope alerts root.

    Returns ``~/.scitex/audit/github-alerts/runtime/`` (or
    ``$SCITEX_DIR/audit/github-alerts/runtime/`` when ``SCITEX_DIR`` is set).
    """
    return _scitex_dir() / PKG_SHORT / ALERTS_SUBDIR / "runtime"


def _resolve_project_scope() -> Path | None:
    """Project-scope root, if inside a git repo.

    Returns ``<project>/.scitex/audit/github-alerts/runtime/`` or ``None``.
    """
    root = _project_root()
    if root is None:
        return None
    return root / ".scitex" / PKG_SHORT / ALERTS_SUBDIR / "runtime"


def _get_primary_alerts_dir() -> Path:
    """Resolve the primary alerts directory with full precedence chain.

    Precedence (highest first):

    1. ``$SCITEX_AUDIT_DIR`` env var
    2. Project scope  (``<project>/.scitex/audit/github-alerts/runtime/``)
    3. User scope     (``~/.scitex/audit/github-alerts/runtime/``)
    """
    env = os.environ.get("SCITEX_AUDIT_DIR")
    if env:
        # Honour the env var verbatim — operator chose the location;
        # don't append the ALERTS_SUBDIR on top of an explicit path.
        return Path(env).expanduser().resolve()

    project = _resolve_project_scope()
    if project is not None:
        return project

    return _resolve_user_scope()


# ---------------------------------------------------------------------------
# Legacy migration: pre-v0.2 CWD-relative (carried over from scitex-security)
# ---------------------------------------------------------------------------


def _legacy_rel_alerts_dir_exists() -> bool:
    """Check if the old CWD-relative ``./logs/security`` exists."""
    return _LEGACY_REL_ALERTS_DIR.is_dir()


def _migrate_from_legacy_rel(primary: Path) -> None:
    """One-time migration: move ``./logs/security/*`` → *primary*.

    Only runs if *primary* was not previously migrated (marker file
    guard). Emits a ``DeprecationWarning`` on first occurrence.
    """
    if not _legacy_rel_alerts_dir_exists():
        return

    marker = primary / _LEGACY_REL_MARKER
    if marker.exists():
        return

    legacy = _LEGACY_REL_ALERTS_DIR.resolve()
    warnings.warn(
        f"DEPRECATED: {legacy} is deprecated. "
        f"Alert files are now written to {primary}. "
        f"Set $SCITEX_AUDIT_DIR to override.",
        DeprecationWarning,
        stacklevel=3,
    )

    primary.mkdir(parents=True, exist_ok=True)
    for f in legacy.glob("security-*.txt"):
        shutil.move(str(f), str(primary / f.name))

    # Clean up the old symlink if it exists
    old_link = legacy / "security-latest.txt"
    if old_link.is_symlink() or old_link.exists():
        old_link.unlink()

    marker.touch()


def _check_legacy_fallback_read(target_dir: Path | None) -> Path | None:
    """If *target_dir* is the default and the legacy dir exists, return it.

    Keeps the old path readable for one minor version per §8 of the
    local-state-directories convention. Guards against infinite loops
    because ``get_latest_alerts_file`` is the caller in that path.
    """
    if target_dir is not None:
        return target_dir
    if _legacy_rel_alerts_dir_exists():
        return _LEGACY_REL_ALERTS_DIR.resolve()
    return None


# ---------------------------------------------------------------------------
# Legacy migration: ~/.scitex/security/ (from absorbed scitex-security 0.1.x)
# ---------------------------------------------------------------------------


def _legacy_security_user_dir() -> Path:
    """Path that scitex-security 0.1.x wrote to under the SciTeX root."""
    return _scitex_dir() / _LEGACY_USER_SECURITY_SUBDIR


def _migrate_legacy_security_dir() -> None:
    """One-shot migration of ``~/.scitex/security/`` → ``~/.scitex/audit/github-alerts/``.

    Runs automatically on package import (called from
    ``scitex_audit/__init__.py``). Guarded by a marker file so it only
    fires once per user. Per ADR-0001 §"Locked decisions": NO manual
    user step. Prefers ``os.symlink`` so users keep one storage
    location; falls back to ``shutil.move`` when symlinks aren't
    available on the platform (e.g. Windows without dev-mode).

    No-ops if the legacy dir doesn't exist, or if the absorbing dir
    already exists, or if the marker file says we already migrated.
    Wrapped in try/except by the caller; this body itself only raises
    on genuinely-unexpected filesystem corruption.
    """
    legacy = _legacy_security_user_dir()
    if not legacy.exists():
        return

    audit_root = _scitex_dir() / PKG_SHORT
    marker = audit_root / _LEGACY_SECURITY_USER_MARKER
    if marker.exists():
        return

    target = audit_root / ALERTS_SUBDIR
    if target.exists():
        # The new location already has data — operator has migrated
        # manually or run scitex-audit before. Record the marker so we
        # don't keep re-checking.
        audit_root.mkdir(parents=True, exist_ok=True)
        marker.touch()
        return

    audit_root.mkdir(parents=True, exist_ok=True)

    moved = False
    try:
        os.symlink(legacy, target)
        logger.info(
            "scitex-audit: linked legacy %s → %s "
            "(per ADR-0001 absorption of scitex-security)",
            legacy,
            target,
        )
        moved = True
    except OSError:
        # Platform doesn't support symlinks (Windows w/o dev mode,
        # cross-device link, etc.). Fall back to a real move.
        try:
            shutil.move(str(legacy), str(target))
            logger.info(
                "scitex-audit: moved legacy %s → %s "
                "(per ADR-0001 absorption of scitex-security)",
                legacy,
                target,
            )
            moved = True
        except OSError as exc:
            # Last-ditch: log + leave both dirs in place. Avoid
            # raising — a path migration glitch must not break import.
            logger.warning(
                "scitex-audit: could not migrate legacy %s → %s: %s. "
                "Continuing with the new location empty; the old data "
                "is still readable at %s.",
                legacy,
                target,
                exc,
                legacy,
            )

    if moved:
        marker.touch()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_default_alerts_dir() -> Path:
    """Return the default alerts directory, creating it if needed.

    Runs the pre-v0.2 CWD-relative migration when the legacy
    ``./logs/security`` directory is detected. The user-scope
    ``~/.scitex/security/`` migration is run separately on package
    import (``_migrate_legacy_security_dir``).
    """
    primary = _get_primary_alerts_dir()
    _migrate_from_legacy_rel(primary)
    primary.mkdir(parents=True, exist_ok=True)
    return primary


__all__ = [
    "PKG_SHORT",
    "ALERTS_SUBDIR",
    "get_default_alerts_dir",
]


# EOF
