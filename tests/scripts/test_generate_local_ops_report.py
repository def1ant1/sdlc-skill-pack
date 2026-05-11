from __future__ import annotations

import json

from scripts.telemetry.generate_local_ops_report import generate_report


def test_generate_report_from_sample_histories(tmp_path):
    workflow_dir = tmp_path / "workflow"
    schedule_dir = tmp_path / "schedule"
    workflow_dir.mkdir()
    schedule_dir.mkdir()

    (workflow_dir / "run-1.json").write_text(json.dumps({
        "run_id": "RUN-1",
        "mode": "local",
        "status": "paused_for_hitl",
        "started_at": "2026-05-10T00:00:00Z",
        "completed_at": "2026-05-10T00:10:00Z",
        "steps": [
            {"step": 1, "skill": "devsecops", "status": "pending_hitl", "tokens_used": 1200}
        ]
    }))
    (schedule_dir / "sched-1.json").write_text(json.dumps({
        "run_id": "SCHED-1",
        "schedule_id": "weekly-ops",
        "run_at": "2026-05-10T00:00:00Z",
        "executed_at": "2026-05-10T00:00:10Z",
        "status": "completed"
    }))

    report = generate_report(workflow_dir, schedule_dir)
    assert len(report["workflow_run_history"]) == 1
    assert len(report["schedule_history"]) == 1
    assert report["pending_governance_approvals"][0]["run_id"] == "RUN-1"
    assert report["token_cost_estimates"]["total_tokens_estimated"] == 1200
    assert report["consistency_checks"]["passed"] is True


def test_consistency_check_flags_missing_ids_and_timestamps(tmp_path):
    workflow_dir = tmp_path / "workflow"
    schedule_dir = tmp_path / "schedule"
    workflow_dir.mkdir()
    schedule_dir.mkdir()

    (workflow_dir / "bad.json").write_text(json.dumps({"status": "completed", "steps": []}))
    report = generate_report(workflow_dir, schedule_dir)
    assert report["consistency_checks"]["passed"] is False
    assert any("missing run_id" in e for e in report["consistency_checks"]["errors"])
    assert any("missing started_at" in e for e in report["consistency_checks"]["errors"])
