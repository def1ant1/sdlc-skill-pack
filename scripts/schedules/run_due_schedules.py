#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json
from pathlib import Path
from typing import Any
from scripts.schedules.preview_schedule import REGISTRY_PATH, compute_due_runs, load_registry, parse_iso
from scripts.schedules.schedule_state import ScheduleStateStore

def _id(schedule_id:str, run_at:dt.datetime)->str: return hashlib.sha256(f'{schedule_id}:{run_at.isoformat()}'.encode()).hexdigest()[:16]

def execute_due(as_of:dt.datetime, registry:Path, state_dir:Path, lookback_minutes:int=60, dry_run:bool=False)->dict[str,Any]:
    store=ScheduleStateStore(state_dir); runs=[]; diagnostics=[]
    for s in load_registry(registry):
        if not s.get('enabled',False): continue
        due=compute_due_runs(s,as_of,lookback_minutes); mis=s.get('misfire_policy','skip')
        if len(due)>1 and mis=='skip': diagnostics.append({'schedule_id':s['schedule_id'],'reason':'misfire_skip'}); due=[]
        elif len(due)>1 and mis=='run_once': due=due[-1:]
        for run_at in due:
            run_id=_id(s['schedule_id'],run_at)
            if store.has_run_record(s['schedule_id'],run_id): runs.append({'schedule_id':s['schedule_id'],'run_id':run_id,'status':'duplicate_skipped'}); continue
            ok,reason=store.acquire_lock(s['schedule_id'],run_id,as_of,s.get('concurrency','forbid'))
            if not ok: diagnostics.append({'schedule_id':s['schedule_id'],'reason':reason}); continue
            rec={'run_id':run_id,'schedule_id':s['schedule_id'],'planner_target':s.get('planner_target'),'owner':s.get('owner','unknown'),'risk_tier':s.get('risk_tier','low'),'run_at':run_at.isoformat(),'executed_at':as_of.isoformat(),'status':'dry_run' if dry_run else 'completed'}
            if not dry_run: store.write_run_record(rec)
            store.release_lock(s['schedule_id'],s.get('concurrency','forbid')); runs.append({'schedule_id':s['schedule_id'],'run_id':run_id,'status':'dry_run' if dry_run else 'executed'})
    return {'as_of':as_of.isoformat(),'dry_run':dry_run,'runs':runs,'diagnostics':diagnostics}

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--registry',type=Path,default=REGISTRY_PATH); ap.add_argument('--state-dir',type=Path,default=Path('runtime')); ap.add_argument('--as-of',default=dt.datetime.now(dt.timezone.utc).isoformat()); ap.add_argument('--lookback-minutes',type=int,default=60); ap.add_argument('--dry-run',action='store_true'); a=ap.parse_args()
    print(json.dumps(execute_due(parse_iso(a.as_of),a.registry,a.state_dir,a.lookback_minutes,a.dry_run),indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
