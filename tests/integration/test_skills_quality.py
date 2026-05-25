"""Enforces SciTeX skills quality checklist §1–§4.

# PS-206b: import-smoke-allowed — dynamically generates test functions
# via scitex_dev._skills_quality_pytest.make_skill_quality_tests().
"""

from pathlib import Path

import pytest

scitex_dev_skills = pytest.importorskip("scitex_dev._skills_quality_pytest")
make_skill_quality_tests = scitex_dev_skills.make_skill_quality_tests

test_skills_quality = make_skill_quality_tests(
    package_root=Path(__file__).resolve().parents[2]
)
