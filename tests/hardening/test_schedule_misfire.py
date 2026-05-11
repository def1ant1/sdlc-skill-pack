from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.schedules.run_due_schedules import execute_due  # noqa: E402


def test_schedule_misfire_skip_and_duplicate_are_deterministic(tmp_path: Path):
    as_of = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)
    schedule = {"schedule_id": "s1", "enabled": True, "misfire_policy": "skip", "concurrency": "forbid"}
    due = [as_of - dt.timedelta(minutes=20), as_of - dt.timedelta(minutes=10)]

    with mock.patch("scripts.schedules.run_due_schedules.load_registry", return_value=[schedule]), \
         mock.patch("scripts.schedules.run_due_schedules.compute_due_runs", return_value=due):
        out = execute_due(as_of, Path("dummy"), tmp_path)
    assert out["runs"] == []
    assert out["diagnostics"][0]["reason"] == "misfire_skip"

    # duplicate path
    with mock.patch("scripts.schedules.run_due_schedules.load_registry", return_value=[{**schedule, "misfire_policy": "run_once"}]), \
         mock.patch("scripts.schedules.run_due_schedules.compute_due_runs", return_value=[as_of]), \
         mock.patch("scripts.schedules.run_due_schedules.ScheduleStateStore.has_run_record", return_value=True):
        out2 = execute_due(as_of, Path("dummy"), tmp_path)
    assert out2["runs"][0]["status"] == "duplicate_skipped"
