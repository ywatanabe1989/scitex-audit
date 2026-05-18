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


@pytest.fixture
def long_findings_results():
    findings = [
        {
            "severity": "MED",
            "file": f"f{i}.py",
            "line": i,
            "message": f"m{i}",
        }
        for i in range(8)
    ]
    return {
        "python": {
            "status": "findings",
            "summary": "many",
            "findings": findings,
        }
    }


class TestFormatText:
    def test_format_text_includes_python_check_name(self, sample_results):
        # Arrange
        results = sample_results
        # Act
        out = format_text(results)
        # Assert
        assert "PYTHON" in out

    def test_format_text_includes_shell_check_name(self, sample_results):
        # Arrange
        results = sample_results
        # Act
        out = format_text(results)
        # Assert
        assert "SHELL" in out

    def test_format_text_includes_deps_check_name(self, sample_results):
        # Arrange
        results = sample_results
        # Act
        out = format_text(results)
        # Assert
        assert "DEPS" in out

    def test_format_text_renders_findings_status_label(self, sample_results):
        # Arrange
        results = sample_results
        # Act
        out = format_text(results)
        # Assert
        assert "FINDINGS" in out

    def test_format_text_renders_ok_status_label(self, sample_results):
        # Arrange
        results = sample_results
        # Act
        out = format_text(results)
        # Assert
        assert "OK" in out

    def test_format_text_renders_skipped_status_label(self, sample_results):
        # Arrange
        results = sample_results
        # Act
        out = format_text(results)
        # Assert
        assert "SKIPPED" in out

    def test_format_text_includes_summary_string(self, sample_results):
        # Arrange
        results = sample_results
        # Act
        out = format_text(results)
        # Assert
        assert "1 issue found" in out

    def test_format_text_includes_finding_message_string(self, sample_results):
        # Arrange
        results = sample_results
        # Act
        out = format_text(results)
        # Assert
        assert "use of assert" in out

    def test_format_text_uppercases_unknown_status_label(self):
        # Arrange
        weird_results = {"weird": {"status": "vroom", "summary": "x"}}
        # Act
        out = format_text(weird_results)
        # Assert
        assert "VROOM" in out

    def test_format_text_includes_first_message_in_long_finding_list(
        self, long_findings_results
    ):
        # Arrange
        results = long_findings_results
        # Act
        out = format_text(results)
        # Assert
        assert "m0" in out

    def test_format_text_includes_fifth_message_in_long_finding_list(
        self, long_findings_results
    ):
        # Arrange
        results = long_findings_results
        # Act
        out = format_text(results)
        # Assert
        assert "m4" in out

    def test_format_text_truncates_after_five_findings_with_summary(
        self, long_findings_results
    ):
        # Arrange
        results = long_findings_results
        # Act
        out = format_text(results)
        # Assert
        assert "and 3 more" in out


class TestFormatJson:
    def test_format_json_returns_parseable_json_dict(self, sample_results):
        # Arrange
        results = sample_results
        # Act
        parsed = json.loads(format_json(results))
        # Assert
        assert isinstance(parsed, dict)

    def test_format_json_envelope_has_expected_top_level_keys(self, sample_results):
        # Arrange
        results = sample_results
        # Act
        parsed = json.loads(format_json(results))
        # Assert
        assert set(parsed.keys()) == {"timestamp", "tool_versions", "results"}

    def test_format_json_results_field_equals_input_results(self, sample_results):
        # Arrange
        results = sample_results
        # Act
        parsed = json.loads(format_json(results))
        # Assert
        assert parsed["results"] == results

    def test_format_json_timestamp_contains_iso_t_separator(self, sample_results):
        # Arrange
        results = sample_results
        # Act
        parsed = json.loads(format_json(results))
        # Assert
        assert "T" in parsed["timestamp"]

    def test_format_json_timestamp_is_timezone_aware_iso_string(self, sample_results):
        # Arrange
        results = sample_results
        # Act
        ts = json.loads(format_json(results))["timestamp"]
        # Assert
        assert ts.endswith("+00:00") or ts.endswith("Z")


class TestFormatFindingLine:
    def test_python_finding_line_includes_severity_token(self):
        # Arrange
        finding = {
            "severity": "LOW",
            "file": "a.py",
            "line": 7,
            "message": "no shebang",
        }
        # Act
        line = _format_finding_line("python", finding)
        # Assert
        assert "LOW" in line

    def test_python_finding_line_includes_file_and_line_colon_pair(self):
        # Arrange
        finding = {
            "severity": "LOW",
            "file": "a.py",
            "line": 7,
            "message": "no shebang",
        }
        # Act
        line = _format_finding_line("python", finding)
        # Assert
        assert "a.py:7" in line

    def test_python_finding_line_includes_message_string(self):
        # Arrange
        finding = {
            "severity": "LOW",
            "file": "a.py",
            "line": 7,
            "message": "no shebang",
        }
        # Act
        line = _format_finding_line("python", finding)
        # Assert
        assert "no shebang" in line

    def test_shell_finding_line_includes_level_label(self):
        # Arrange
        finding = {
            "level": "warning",
            "file": "build.sh",
            "line": 3,
            "code": "2086",
            "message": "double-quote",
        }
        # Act
        line = _format_finding_line("shell", finding)
        # Assert
        assert "warning" in line

    def test_shell_finding_line_includes_file_and_line_colon_pair(self):
        # Arrange
        finding = {
            "level": "warning",
            "file": "build.sh",
            "line": 3,
            "code": "2086",
            "message": "double-quote",
        }
        # Act
        line = _format_finding_line("shell", finding)
        # Assert
        assert "build.sh:3" in line

    def test_shell_finding_line_prefixes_code_with_sc_namespace(self):
        # Arrange
        finding = {
            "level": "warning",
            "file": "build.sh",
            "line": 3,
            "code": "2086",
            "message": "double-quote",
        }
        # Act
        line = _format_finding_line("shell", finding)
        # Assert
        assert "SC2086" in line

    def test_shell_finding_line_includes_message_string(self):
        # Arrange
        finding = {
            "level": "warning",
            "file": "build.sh",
            "line": 3,
            "code": "2086",
            "message": "double-quote",
        }
        # Act
        line = _format_finding_line("shell", finding)
        # Assert
        assert "double-quote" in line

    def test_deps_finding_line_uses_pip_style_package_double_equals_version(
        self,
    ):
        # Arrange
        finding = {
            "package": "requests",
            "version": "2.0.0",
            "vuln_id": "GHSA-x",
        }
        # Act
        line = _format_finding_line("deps", finding)
        # Assert
        assert "requests==2.0.0" in line

    def test_deps_finding_line_includes_vulnerability_id(self):
        # Arrange
        finding = {
            "package": "requests",
            "version": "2.0.0",
            "vuln_id": "GHSA-x",
        }
        # Act
        line = _format_finding_line("deps", finding)
        # Assert
        assert "GHSA-x" in line

    def test_github_finding_line_includes_category_token(self):
        # Arrange
        finding = {"category": "secret-scanning", "summary": "AWS key leaked"}
        # Act
        line = _format_finding_line("github", finding)
        # Assert
        assert "secret-scanning" in line

    def test_github_finding_line_includes_summary_text(self):
        # Arrange
        finding = {"category": "secret-scanning", "summary": "AWS key leaked"}
        # Act
        line = _format_finding_line("github", finding)
        # Assert
        assert "AWS key leaked" in line

    def test_unknown_check_kind_falls_back_to_repr_of_finding(self):
        # Arrange
        finding = {"x": 1}
        # Act
        line = _format_finding_line("mystery", finding)
        # Assert
        assert line == str(finding)


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])

# EOF
