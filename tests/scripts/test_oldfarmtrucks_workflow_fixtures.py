from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = ROOT / "workflows" / "fixtures" / "oldfarmtrucks"
EXECUTOR = ROOT / "scripts" / "runtime" / "execute_workflow.py"


def _load_fixture(path: Path) -> dict:
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_oldfarmtrucks_fixtures_dry_run_and_artifacts() -> None:
    fixture_paths = sorted(FIXTURES_DIR.glob("*.json")) + sorted(FIXTURES_DIR.glob("*.yaml"))
    assert fixture_paths, "Expected workflow fixtures under workflows/fixtures/oldfarmtrucks"

    for fixture_path in fixture_paths:
        fixture = _load_fixture(fixture_path)

        assert fixture["planner_output_ref"].startswith("docs/examples/")
        assert fixture["canonical_governance_policies"], "Fixture missing governance policy refs"
        assert all(isinstance(ref, str) and ref for ref in fixture["canonical_governance_policies"])

        plan = fixture["plan"]
        assert plan["planner"] == "business-workflow-planner"
        assert plan["planning_contract"] == "workflow-plan-v1"
        assert plan["skill_chain"], "Fixture plan missing skill chain"

        plan_path = FIXTURES_DIR / f"{fixture_path.stem}.plan.json"
        plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, str(EXECUTOR), "--plan", str(plan_path), "--dry-run"],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0, result.stderr
            payload = json.loads(result.stdout)
        finally:
            plan_path.unlink(missing_ok=True)

        assert payload["status"] == "dry_run"
        assert payload["run_id"].startswith("DRYRUN-")
        assert len(payload["steps"]) == len(plan["skill_chain"])
        assert all(step["status"] == "dry_run" for step in payload["steps"])

        for artifact_key in fixture["expected_artifacts"]:
            assert artifact_key in payload
