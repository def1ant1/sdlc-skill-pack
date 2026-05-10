import json
import subprocess
from pathlib import Path


def test_validate_skill_evals_rejects_incomplete_p1_spec(tmp_path: Path):
    skill_dir = tmp_path / "skills" / "demo-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        """---
name: demo-skill
priority: P1
---

# Demo
""",
        encoding="utf-8",
    )
    (skill_dir / "eval.spec.json").write_text(
        json.dumps({"priority": "P1", "datasets": [], "metrics": [{"name": "x"}], "acceptance_gates": []}),
        encoding="utf-8",
    )

    run = subprocess.run(["python", "scripts/validate_skill_evals.py", str(tmp_path)], capture_output=True, text=True)
    assert run.returncode == 1
    assert "datasets must be a non-empty list" in run.stdout
    assert "acceptance_gates must be a non-empty list" in run.stdout


def test_validate_telemetry_requires_correlation_id_for_runtime_and_business(tmp_path: Path):
    bad = [
        {"event_category": "runtime", "tenant_id": "t1", "workflow_id": "w1"},
        {"event_category": "business", "correlation_id": "", "tenant_id": "t1", "workflow_id": "w1"},
    ]
    p = tmp_path / "events.json"
    p.write_text(json.dumps(bad), encoding="utf-8")

    run = subprocess.run(["python", "scripts/validate_telemetry_events.py", str(p)], capture_output=True, text=True)
    assert run.returncode == 1
    assert "missing correlation_id" in run.stdout
