"""
Tests for scripts/orchestration/detect_skill_gaps.py

Covers gap detection accuracy, false-positive suppression for known aliases,
and the alignment-testing path filter fix.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
DETECTOR = REPO_ROOT / "scripts" / "orchestration" / "detect_skill_gaps.py"


def detect(target_dir: Path | None = None) -> dict:
    cmd = [sys.executable, str(DETECTOR)]
    if target_dir:
        cmd.append(str(target_dir))
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(target_dir or REPO_ROOT))
    assert result.returncode == 0, f"detect_skill_gaps.py failed:\n{result.stderr}"
    return json.loads(result.stdout)


def make_skill(base: Path, name: str, deps: list[str] | None = None) -> None:
    skill_dir = base / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    if deps:
        deps_list = "\n".join(f"    - {d}" for d in deps)
        meta_yaml = f"\nmetadata:\n  dependencies:\n{deps_list}"
    else:
        meta_yaml = "\nmetadata:\n  dependencies: []"
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Test skill{meta_yaml}\n---\n"
    )


# ---------------------------------------------------------------------------
# Live repo regression
# ---------------------------------------------------------------------------

class TestLiveRepo:
    def test_no_false_positive_on_alignment_testing(self):
        """skills/alignment-testing must NOT be filtered out as a test directory."""
        alignment_path = REPO_ROOT / "skills" / "alignment-testing"
        if not alignment_path.exists():
            pytest.skip("skills/alignment-testing not present in this repo")
        out = detect()
        registered = out.get("registered_skills", [])
        assert "alignment-testing" in registered, (
            "alignment-testing was incorrectly filtered as a test directory"
        )

    def test_known_aliases_not_flagged_as_missing(self):
        """gtm-orchestration and other aliases must not appear in missing_dependencies."""
        out = detect()
        missing = out.get("missing_dependencies", [])
        known_aliases = {"gtm-orchestration", "connector-hub", "sdlc-orchestration"}
        flagged = [m for m in missing if m in known_aliases]
        assert not flagged, f"Known aliases incorrectly flagged as missing: {flagged}"

    def test_output_has_required_keys(self):
        out = detect()
        for key in ("registered_skills", "missing_skills", "missing_dependencies"):
            assert key in out, f"Missing output key: {key}"

    def test_registered_skills_is_list(self):
        out = detect()
        assert isinstance(out["registered_skills"], list)

    def test_no_test_dirs_in_registered_skills(self):
        """Directories named 'tests', 'test', '__pycache__' must not appear as skills."""
        out = detect()
        bad = [s for s in out.get("registered_skills", [])
               if s in {"tests", "test", "__pycache__"}]
        assert not bad, f"Test directories appeared as registered skills: {bad}"


# ---------------------------------------------------------------------------
# Synthetic fixture tests
# ---------------------------------------------------------------------------

class TestSyntheticGapDetection:
    def test_no_gaps_in_clean_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, "skill-a")
            make_skill(root, "skill-b", deps=["skill-a"])
            out = detect(root)
            assert out["missing_dependencies"] == []

    def test_missing_dependency_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, "skill-a", deps=["skill-nonexistent"])
            out = detect(root)
            assert "skill-nonexistent" in out["missing_dependencies"]

    def test_test_dir_excluded_from_skills(self):
        """A directory named 'tests' inside skills/ must not register as a skill."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, "real-skill")
            tests_dir = root / "skills" / "tests"
            tests_dir.mkdir(parents=True)
            (tests_dir / "SKILL.md").write_text(
                "---\nname: tests\ndescription: Should not register\n---\n"
            )
            out = detect(root)
            assert "tests" not in out["registered_skills"]

    def test_skill_with_test_in_name_not_excluded(self):
        """A skill like 'alignment-testing' must be registered normally."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, "alignment-testing")
            out = detect(root)
            assert "alignment-testing" in out["registered_skills"]