#!/usr/bin/env python3
from __future__ import annotations
import datetime as dt, json
from pathlib import Path
from typing import Any

class ScheduleStateStore:
    def __init__(self, root: Path) -> None:
        self.root = root; self.locks_dir = root / 'locks'; self.history_dir = root / 'history'
        self.locks_dir.mkdir(parents=True, exist_ok=True); self.history_dir.mkdir(parents=True, exist_ok=True)
    def _lock_path(self, schedule_id: str) -> Path: return self.locks_dir / f'{schedule_id}.lock.json'
    def acquire_lock(self, schedule_id: str, run_key: str, now: dt.datetime, mode: str) -> tuple[bool, str | None]:
        p = self._lock_path(schedule_id)
        if p.exists():
            if mode == 'forbid': return False, 'active_lock'
            if mode == 'replace': p.unlink(missing_ok=True)
            if mode == 'allow': return True, None
        p.write_text(json.dumps({'schedule_id': schedule_id,'run_key': run_key,'acquired_at': now.isoformat()}, indent=2, sort_keys=True)+'\n'); return True, None
    def release_lock(self, schedule_id: str, mode: str) -> None:
        if mode != 'allow': self._lock_path(schedule_id).unlink(missing_ok=True)
    def run_artifact_path(self, schedule_id: str, run_key: str) -> Path: return self.history_dir / schedule_id / f'{run_key}.json'
    def has_run_record(self, schedule_id: str, run_key: str) -> bool: return self.run_artifact_path(schedule_id, run_key).exists()
    def write_run_record(self, payload: dict[str, Any]) -> Path:
        p = self.run_artifact_path(payload['schedule_id'], payload['run_key']); p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(payload, indent=2, sort_keys=True)+'\n'); return p
