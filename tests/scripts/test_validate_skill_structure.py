"""
Tests for scripts/validation/validate_skill_structure.py

Runs the validator against real repo layout and synthetic fixtures.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
VALIDATOR = REPO_ROOT / "scripts" / "validation" / "validate_skill_structure.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_validator(target_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(target_dir)],
        capture_output=True,
        text=True,
    )


def make_skill(base: Path, name: str, with_skill_md: bool = True) -> Path:
    skill_dir = base / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    if with_skill_md:
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Test skill for {name}\n---\n"
        )
    return skill_dir


# ---------------------------------------------------------------------------
# Live repo tests
# ---------------------------------------------------------------------------

class TestLiveRepo:
    def test_validator_exits_zero_on_real_repo(self):
        """Validator must pass on the actual repository without errors."""
        result = run_validator(REPO_ROOT)
        assert result.returncode == 0, (
            f"validate_skill_structure failed on real repo:\n{result.stdout}\n{result.stderr}"
        )

    def test_all_skill_dirs_are_kebab_case(self):
        skills_root = REPO_ROOT / "skills"
        for entry in skills_root.iterdir():
            if entry.is_dir() and not entry.name.startswith("."):
                assert entry.name == entry.name.lower(), (
                    f"Skill dir not lowercase: {entry.name}"
                )
                assert "_" not in entry.name, (
                    f"Skill dir uses underscores (must be kebab-case): {entry.name}"
                )

    def test_all_skill_dirs_have_skill_md(self):
        skills_root = REPO_ROOT / "skills"
        missing = [
            entry.name
            for entry in skills_root.iterdir()
            if entry.is_dir()
            and not entry.name.startswith(".")
            and not (entry / "SKILL.md").exists()
        ]
        assert not missing, f"Skill dirs missing SKILL.md: {missing}"

    def test_all_core_dirs_have_skill_md(self):
        core_root = REPO_ROOT / "core"
        missing = [
            entry.name
            for entry in core_root.iterdir()
            if entry.is_dir()
            and not entry.name.startswith(".")
            and not (entry / "SKILL.md").exists()
        ]
        assert not missing, f"Core dirs missing SKILL.md: {missing}"


# ---------------------------------------------------------------------------
# Synthetic fixture tests
# ---------------------------------------------------------------------------

class TestSyntheticFixtures:
    def test_valid_structure_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, "my-skill")
            make_skill(root, "another-skill")
            result = run_validator(root)
            assert result.returncode == 0

    def test_missing_skill_md_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, "valid-skill")
            make_skill(root, "broken-skill", with_skill_md=False)
            result = run_validator(root)
            assert result.returncode != 0

    def test_non_kebab_case_dir_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad_dir = root / "skills" / "MySkill"
            bad_dir.mkdir(parents=True)
            (bad_dir / "SKILL.md").write_text("---\nname: MySkill\ndescription: bad\n---\n")
            result = run_validator(root)
            assert result.returncode != 0

    def test_underscore_in_name_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad_dir = root / "skills" / "my_skill"
            bad_dir.mkdir(parents=True)
            (bad_dir / "SKILL.md").write_text("---\nname: my_skill\ndescription: bad\n---\n")
            result = run_validator(root)
            assert result.returncode != 0

    def test_empty_skills_dir_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills").mkdir()
            result = run_validator(root)
            assert result.returncode == 0