#!/usr/bin/env python3
"""Tests for scitex_audit._format formatters.

Covers the public surface used by the CLI:
  - format_text(): per-check banner with status badge
  - format_json(): valid JSON with timestamp / tool_versions / results
  - _format_finding_line(): per-check finding rendering for python / shell /
    deps / github / unknown
"""

import json

import pytest

from scitex_audit._format import (
    _format_finding_line,
    format_json,
    format_text,
)


@pytest.fixture
def sample_results():
    return {
        "python": {
            "status": "findings",
            "summary": "1 issue found",
            "findings": [
                {
                    "severity": "HIGH",
                    "file": "src/foo.py",
                    "line": 12,
                    "message": "use of assert",
                }
            ],
        },
        "shell": {
            "status": "ok",
            "summary": "no issues",
            "findings": [],
        },
        "deps": {
            "status": "skipped",
            "summary": "pip-audit not installed",
            "findings": [],
        },
    }


class TestFormatText:
    def test_includes_each_check_name(self, sample_results):
        out = format_text(sample_results)
        # ANSI color codes may wrap names — check uppercase basenames appear
        assert "PYTHON" in out
        assert "SHELL" in out
        assert "DEPS" in out

    def test_renders_known_status_labels(self, sample_results):
        out = format_text(sample_results)
        assert "FINDINGS" in out
        assert "OK" in out
        assert "SKIPPED" in out

    def test_includes_summary_and_finding_message(self, sample_results):
        out = format_text(sample_results)
        assert "1 issue found" in out
        assert "use of assert" in out

    def test_unknown_status_is_uppercased_not_swallowed(self):
        out = format_text({"weird": {"status": "vroom", "summary": "x"}})
        assert "VROOM" in out

    def test_truncates_long_finding_lists(self):
        # Build 8 findings — formatter caps at 5 + "and N more"
        findings = [
            {
                "severity": "MED",
                "file": f"f{i}.py",
                "line": i,
                "message": f"m{i}",
            }
            for i in range(8)
        ]
        out = format_text(
            {
                "python": {
                    "status": "findings",
                    "summary": "many",
                    "findings": findings,
                }
            }
        )
        # 5 shown, 3 hidden behind "and 3 more"
        assert "m0" in out and "m4" in out
        assert "and 3 more" in out


class TestFormatJson:
    def test_returns_valid_json(self, sample_results):
        out = format_json(sample_results)
        parsed = json.loads(out)
        assert isinstance(parsed, dict)

    def test_envelope_shape(self, sample_results):
        parsed = json.loads(format_json(sample_results))
        assert set(parsed.keys()) == {"timestamp", "tool_versions", "results"}
        assert parsed["results"] == sample_results

    def test_timestamp_is_iso_with_tz(self, sample_results):
        parsed = json.loads(format_json(sample_results))
        ts = parsed["timestamp"]
        assert "T" in ts
        # tz-aware iso ends in +00:00 (utc) or Z
        assert ts.endswith("+00:00") or ts.endswith("Z")


class TestFormatFindingLine:
    def test_python_includes_severity_file_line_msg(self):
        line = _format_finding_line(
            "python",
            {
                "severity": "LOW",
                "file": "a.py",
                "line": 7,
                "message": "no shebang",
            },
        )
        assert "LOW" in line
        assert "a.py:7" in line
        assert "no shebang" in line

    def test_shell_renders_sc_code(self):
        line = _format_finding_line(
            "shell",
            {
                "level": "warning",
                "file": "build.sh",
                "line": 3,
                "code": "2086",
                "message": "double-quote",
            },
        )
        assert "warning" in line
        assert "build.sh:3" in line
        assert "SC2086" in line
        assert "double-quote" in line

    def test_deps_uses_package_version_vulnid(self):
        line = _format_finding_line(
            "deps",
            {
                "package": "requests",
                "version": "2.0.0",
                "vuln_id": "GHSA-x",
            },
        )
        assert "requests==2.0.0" in line
        assert "GHSA-x" in line

    def test_github_uses_category_summary(self):
        line = _format_finding_line(
            "github",
            {"category": "secret-scanning", "summary": "AWS key leaked"},
        )
        assert "secret-scanning" in line
        assert "AWS key leaked" in line

    def test_unknown_check_falls_back_to_str(self):
        finding = {"x": 1}
        line = _format_finding_line("mystery", finding)
        assert line == str(finding)


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])

# EOF
