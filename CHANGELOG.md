# Changelog

All notable changes to `scitex-audit` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] — 2026-06-07

### Added
- Absorbed `scitex-security`'s GitHub-alerts checker as the new public
  submodule `scitex_audit.github`. Five public symbols are re-exported
  at the package root: `check_github_alerts`, `save_alerts_to_file`,
  `get_latest_alerts_file`, `format_alerts_report`,
  `GitHubSecurityError`. Behaviour is identical to scitex-security
  0.1.4 (the source was ported verbatim, including the no-mocks
  collaborator-injection signatures).
- New `scitex-audit` console script (`[project.scripts]`) with a click
  group. `scitex-audit github [--repo OWNER/NAME] [--save]` is the new
  CLI surface; it replaces the absorbed `scitex-security` script per
  ADR-0001's noun-verb decision.
- `scitex_audit._paths` — local-state path resolution honouring
  `$SCITEX_AUDIT_DIR`, project scope, and user scope. Default user-scope
  location is `~/.scitex/audit/github-alerts/runtime/`.
- One-shot auto-migration of legacy `~/.scitex/security/` →
  `~/.scitex/audit/github-alerts/` on first import after upgrade.
  Symlink-preferred, move-fallback for platforms without symlinks; a
  marker file prevents re-running. No manual user step required.

### Changed
- `scitex_audit._github.run_github_check` now delegates to the native
  `scitex_audit.github.check_github_alerts` — the soft `try: from
  scitex_security …` happy-path AND the inlined `gh` CLI fallback in
  the `except ImportError` block have BOTH been removed (no
  transitional shim; same-wave migration per ADR-0001's no-tombstones
  rule).
- `scitex-audit` gains a hard runtime dependency on `click>=8.0`
  (previously a dev-only dep) because the new CLI surface needs it at
  runtime.

### Migration
- Users on scitex-security 0.1.x should `pip install scitex-audit>=0.2.0`
  and switch `from scitex_security import …` → `from scitex_audit.github
  import …`. The `scitex.security` umbrella shim (in scitex-python) is
  repointed to `scitex_audit.github` in the same release wave so users
  on the umbrella don't need to touch their imports.
- The `scitex-security` console script becomes a hard-error redirect
  in `scitex-security` 0.2.0 (skill 11 §5 pattern). Re-run as
  `scitex-audit github`.

### Reference
- ADR-0001 in scitex-dev (`docs/adr/0001-absorb-scitex-security-into-scitex-audit.md`,
  PR ywatanabe1989/scitex-dev#139).

## [0.1.4]

- Initial CHANGELOG entry — see git log for prior history.
