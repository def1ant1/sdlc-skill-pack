"""
Tests for scripts/validation/validate_frontmatter.py

Validates YAML frontmatter parsing against the live repo and synthetic inputs.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
VALIDATOR = REPO_ROOT / "scripts" / "validation" / "validate_frontmatter.py"


def run_validator(target_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(target_dir)],
        capture_output=True,
        text=True,
    )


def write_skill(base: Path, name: str, frontmatter: str) -> Path:
    skill_dir = base / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(frontmatter + "\n\n# Body\n")
    return skill_dir


VALID_FM = """\
---
name: test-skill
description: A valid test skill for unit testing
metadata:
  version: "1.0.0"
  category: testing
  owner: platform
  maturity: alpha
  dependencies: []
---"""


# ---------------------------------------------------------------------------
# Live repo
# ---------------------------------------------------------------------------

class TestLiveRepo:
    def test_frontmatter_passes_on_real_repo(self):
        result = run_validator(REPO_ROOT)
        assert result.returncode == 0, (
            f"validate_frontmatter failed on real repo:\n{result.stdout}\n{result.stderr}"
        )

    def test_all_skill_md_have_name_field(self):
        import yaml

        for path in (REPO_ROOT / "skills").rglob("SKILL.md"):
            text = path.read_text(encoding="utf-8")
            if not text.startswith("---"):
                continue
            end = text.index("---", 3)
            fm = yaml.safe_load(text[3:end])
            assert "name" in fm, f"Missing 'name' field in {path}"

    def test_all_skill_md_have_description_field(self):
        import yaml

        for path in (REPO_ROOT / "skills").rglob("SKILL.md"):
            text = path.read_text(encoding="utf-8")
            if not text.startswith("---"):
                continue
            end = text.index("---", 3)
            fm = yaml.safe_load(text[3:end])
            assert "description" in fm, f"Missing 'description' field in {path}"

    def test_no_angle_brackets_in_frontmatter(self):
        for path in list((REPO_ROOT / "skills").rglob("SKILL.md")) + \
                    list((REPO_ROOT / "core").rglob("SKILL.md")):
            text = path.read_text(encoding="utf-8")
            if not text.startswith("---"):
                continue
            end = text.index("---", 3)
            fm_section = text[3:end]
            assert "<" not in fm_section and ">" not in fm_section, (
                f"Angle brackets found in frontmatter of {path}"
            )

    def test_description_max_length(self):
        import yaml

        for path in (REPO_ROOT / "skills").rglob("SKILL.md"):
            text = path.read_text(encoding="utf-8")
            if not text.startswith("---"):
                continue
            end = text.index("---", 3)
            fm = yaml.safe_load(text[3:end])
            desc = fm.get("description", "")
            assert len(desc) <= 1024, (
                f"Description exceeds 1024 chars in {path}: {len(desc)} chars"
            )


# ---------------------------------------------------------------------------
# Synthetic fixtures
# ---------------------------------------------------------------------------

class TestSyntheticFixtures:
    def test_valid_frontmatter_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_skill(Path(tmp), "test-skill", VALID_FM)
            result = run_validator(Path(tmp))
            assert result.returncode == 0

    def test_missing_opening_delimiter_fails(self):
        bad = "name: test-skill\ndescription: oops no delimiter\n---"
        with tempfile.TemporaryDirectory() as tmp:
            write_skill(Path(tmp), "bad-skill", bad)
            result = run_validator(Path(tmp))
            assert result.returncode != 0

    def test_missing_closing_delimiter_fails(self):
        bad = "---\nname: test-skill\ndescription: no closing delimiter"
        with tempfile.TemporaryDirectory() as tmp:
            write_skill(Path(tmp), "bad-skill", bad)
            result = run_validator(Path(tmp))
            assert result.returncode != 0

    def test_missing_name_fails(self):
        bad = "---\ndescription: No name field here\n---"
        with tempfile.TemporaryDirectory() as tmp:
            write_skill(Path(tmp), "bad-skill", bad)
            result = run_validator(Path(tmp))
            assert result.returncode != 0

    def test_missing_description_fails(self):
        bad = "---\nname: no-desc\n---"
        with tempfile.TemporaryDirectory() as tmp:
            write_skill(Path(tmp), "bad-skill", bad)
            result = run_validator(Path(tmp))
            assert result.returncode != 0

    def test_angle_brackets_in_description_fails(self):
        bad = "---\nname: angle-skill\ndescription: Replace <this> with value\n---"
        with tempfile.TemporaryDirectory() as tmp:
            write_skill(Path(tmp), "bad-skill", bad)
            result = run_validator(Path(tmp))
            assert result.returncode != 0

    def test_name_not_kebab_case_fails(self):
        bad = "---\nname: NotKebabCase\ndescription: Bad name format\n---"
        with tempfile.TemporaryDirectory() as tmp:
            write_skill(Path(tmp), "bad-skill", bad)
            result = run_validator(Path(tmp))
            assert result.returncode != 0