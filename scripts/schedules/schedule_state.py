#!/usr/bin/env python3
from __future__ import annotations
import datetime as dt, json
from pathlib import Path
from typing import Any

class ScheduleStateStore:
    def __init__(self, root: Path) -> None:
        self.root=root; self.locks_dir=root/'locks'; self.history_dir=root/'schedule_runs'
        self.locks_dir.mkdir(parents=True, exist_ok=True); self.history_dir.mkdir(parents=True, exist_ok=True)
    def _lock_path(self, schedule_id:str)->Path: return self.locks_dir/f'{schedule_id}.lock.json'
    def acquire_lock(self, schedule_id:str, run_id:str, now:dt.datetime, policy:str)->tuple[bool,str|None]:
        p=self._lock_path(schedule_id)
        if p.exists():
            if policy=='forbid': return False,'active_lock'
            if policy=='replace': p.unlink(missing_ok=True)
            if policy=='allow': return True,None
        p.write_text(json.dumps({'schedule_id':schedule_id,'run_id':run_id,'acquired_at':now.isoformat()},indent=2)+'\n'); return True,None
    def release_lock(self, schedule_id:str, policy:str)->None:
        if policy!='allow': self._lock_path(schedule_id).unlink(missing_ok=True)
    def run_artifact_path(self,schedule_id:str,run_id:str)->Path: return self.history_dir/schedule_id/f'{run_id}.json'
    def has_run_record(self,schedule_id:str,run_id:str)->bool: return self.run_artifact_path(schedule_id,run_id).exists()
    def write_run_record(self,payload:dict[str,Any])->Path:
        p=self.run_artifact_path(payload['schedule_id'],payload['run_id']); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n'); return p
