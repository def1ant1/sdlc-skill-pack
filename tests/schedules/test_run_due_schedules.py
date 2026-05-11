import datetime as dt
from pathlib import Path
import yaml

from scripts.schedules.run_due_schedules import execute_due
from scripts.schedules.preview_schedule import parse_iso


def _write_registry(path: Path, misfire='catch_up', concurrency='forbid'):
    payload={"schedules":[{"schedule_id":"sched-1","enabled":True,"mode":"interval","interval_minutes":15,"planner_target":"plan_business_workflow.py","timezone":"UTC","misfire_policy":misfire,"concurrency":concurrency}]}
    path.write_text(yaml.safe_dump(payload))


def test_deterministic_frozen_time_runs(tmp_path):
    reg=tmp_path/'registry.yaml'; _write_registry(reg)
    as_of=parse_iso('2026-01-01T01:00:00Z')
    result=execute_due(as_of, reg, tmp_path/'state', lookback_minutes=45)
    assert len([r for r in result['runs'] if r['status']=='executed']) == 4


def test_duplicate_run_prevention(tmp_path):
    reg=tmp_path/'registry.yaml'; _write_registry(reg)
    as_of=parse_iso('2026-01-01T01:00:00Z')
    first=execute_due(as_of, reg, tmp_path/'state', lookback_minutes=30)
    second=execute_due(as_of, reg, tmp_path/'state', lookback_minutes=30)
    assert any(r['status']=='executed' for r in first['runs'])
    assert any(r['status']=='duplicate_skipped' for r in second['runs'])


def test_misfire_skip(tmp_path):
    reg=tmp_path/'registry.yaml'; _write_registry(reg, misfire='skip')
    as_of=parse_iso('2026-01-01T01:00:00Z')
    result=execute_due(as_of, reg, tmp_path/'state', lookback_minutes=45)
    assert result['runs'] == []
    assert any(d['reason']=='misfire_skip' for d in result['diagnostics'])
