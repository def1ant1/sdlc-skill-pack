#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json
from pathlib import Path
from scripts.schedules.preview_schedule import REGISTRY_PATH, compute_due_runs, load_registry, parse_iso
from scripts.schedules.schedule_state import ScheduleStateStore

def _key(schedule_id:str, run_at:dt.datetime)->str: return hashlib.sha256(f'{schedule_id}:{run_at.isoformat()}'.encode()).hexdigest()[:16]

def execute_due(as_of: dt.datetime, registry: Path, state_dir: Path, lookback_minutes: int = 60) -> dict:
    store=ScheduleStateStore(state_dir); runs=[]; diagnostics=[]
    for s in load_registry(registry):
        if not s.get('enabled',False): continue
        due=compute_due_runs(s, as_of, lookback_minutes)
        mis=s.get('misfire_policy','skip')
        if len(due)>1 and mis=='skip': diagnostics.append({'schedule_id':s['schedule_id'],'reason':'misfire_skip'}); due=[]
        elif len(due)>1 and mis=='run_once': due=due[-1:]
        for run_at in due:
            key=_key(s['schedule_id'], run_at)
            if store.has_run_record(s['schedule_id'], key): runs.append({'schedule_id':s['schedule_id'],'run_key':key,'status':'duplicate_skipped'}); continue
            ok, reason=store.acquire_lock(s['schedule_id'], key, as_of, s.get('concurrency','forbid'))
            if not ok: diagnostics.append({'schedule_id':s['schedule_id'],'reason':reason}); continue
            store.write_run_record({'run_key':key,'schedule_id':s['schedule_id'],'run_at':run_at.isoformat(),'executed_at':as_of.isoformat(),'status':'completed'})
            store.release_lock(s['schedule_id'], s.get('concurrency','forbid')); runs.append({'schedule_id':s['schedule_id'],'run_key':key,'status':'executed'})
    return {'as_of':as_of.isoformat(),'runs':runs,'diagnostics':diagnostics}

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--registry',type=Path,default=REGISTRY_PATH); ap.add_argument('--state-dir',type=Path,default=Path('runtime/schedule_state')); ap.add_argument('--as-of',default=dt.datetime.now(dt.timezone.utc).isoformat()); ap.add_argument('--lookback-minutes',type=int,default=60); a=ap.parse_args()
    print(json.dumps(execute_due(parse_iso(a.as_of), a.registry, a.state_dir, a.lookback_minutes), indent=2, sort_keys=True)); return 0

if __name__=='__main__': raise SystemExit(main())
