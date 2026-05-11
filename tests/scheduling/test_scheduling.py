from __future__ import annotations

import datetime as dt

import pytest

from scripts.scheduling.preview_schedule import compute_due_runs
from scripts.scheduling.run_due_schedules import execute_due


def _utc(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def test_due_run_computation_interval_and_cron():
    as_of = _utc("2026-01-05T10:00:00Z")
    interval_schedule = {"schedule_id": "x", "mode": "interval", "interval_minutes": 30, "enabled": True}
    cron_schedule = {"schedule_id": "y", "mode": "cron", "cron": "0 10 * * 1", "enabled": True}

    interval_due = compute_due_runs(interval_schedule, as_of, lookback_minutes=60)
    cron_due = compute_due_runs(cron_schedule, as_of, lookback_minutes=60)

    assert [d.isoformat() for d in interval_due] == [
        "2026-01-05T09:00:00+00:00",
        "2026-01-05T09:30:00+00:00",
        "2026-01-05T10:00:00+00:00",
    ]
    assert [d.isoformat() for d in cron_due] == ["2026-01-05T10:00:00+00:00"]


def test_replay_determinism(tmp_path):
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        """
schedules:
  - schedule_id: deterministic
    mode: interval
    interval_minutes: 60
    enabled: true
    owner: ops
    planner_target: scripts/orchestration/plan_workflow.py
    risk_tier: low
""".strip()
    )
    as_of = _utc("2026-01-05T12:00:00Z")

    out1 = execute_due(as_of, registry, tmp_path / "history", lookback_minutes=120)
    out2 = execute_due(as_of, registry, tmp_path / "history", lookback_minutes=120)

    ids1 = [r["run_id"] for r in out1["runs"]]
    ids2 = [r["run_id"] for r in out2["runs"]]
    assert ids1 == ids2


def test_idempotent_behavior(tmp_path):
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        """
schedules:
  - schedule_id: idempotent
    mode: interval
    interval_minutes: 60
    enabled: true
    owner: ops
    planner_target: scripts/orchestration/plan_workflow.py
    risk_tier: low
""".strip()
    )
    history = tmp_path / "history"
    as_of = _utc("2026-01-05T12:00:00Z")

    first = execute_due(as_of, registry, history, lookback_minutes=60)
    second = execute_due(as_of, registry, history, lookback_minutes=60)

    assert {r["status"] for r in first["runs"]} == {"executed"}
    assert {r["status"] for r in second["runs"]} == {"skipped_existing"}


def test_schedule_artifact_structure_and_required_fields(tmp_path):
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        """
schedules:
  - schedule_id: artifact-shape
    mode: interval
    interval_minutes: 60
    enabled: true
    owner: ops
    planner_target: scripts/orchestration/plan_workflow.py
    risk_tier: low
""".strip()
    )
    history = tmp_path / "history"
    as_of = _utc("2026-01-05T12:00:00Z")

    report = execute_due(as_of, registry, history, lookback_minutes=60)
    run = report["runs"][0]
    artifact_path = history / "artifact-shape" / f"{run['run_id']}.json"

    assert artifact_path.exists()
    payload = __import__("json").loads(artifact_path.read_text())
    assert set(("run_id", "schedule_id", "planner_target", "owner", "risk_tier", "run_at", "executed_at", "status")).issubset(payload.keys())


def test_due_runs_are_deterministic_for_same_inputs():
    as_of = _utc("2026-01-05T10:00:00Z")
    schedule = {"schedule_id": "stable", "mode": "cron", "cron": "0 10 * * 1", "enabled": True}

    first = compute_due_runs(schedule, as_of, lookback_minutes=60)
    second = compute_due_runs(schedule, as_of, lookback_minutes=60)

    assert [d.isoformat() for d in first] == [d.isoformat() for d in second]


def test_invalid_schedule_mode_raises():
    as_of = _utc("2026-01-05T10:00:00Z")
    bad = {"schedule_id": "bad", "mode": "unknown", "enabled": True}

    with pytest.raises(KeyError):
        compute_due_runs(bad, as_of, lookback_minutes=60)
