"""Enforces SciTeX skills quality checklist §1–§4."""

from pathlib import Path

import pytest

scitex_dev_skills = pytest.importorskip("scitex_dev._skills_quality_pytest")
make_skill_quality_tests = scitex_dev_skills.make_skill_quality_tests

test_skills_quality = make_skill_quality_tests(
    package_root=Path(__file__).resolve().parents[2]
)
