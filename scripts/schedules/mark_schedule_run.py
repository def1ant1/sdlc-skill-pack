#!/usr/bin/env python3
from __future__ import annotations
import argparse,datetime as dt,hashlib,json
from pathlib import Path
from scripts.schedules.schedule_state import ScheduleStateStore

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--schedule-id',required=True); ap.add_argument('--run-at',required=True); ap.add_argument('--state-dir',type=Path,default=Path('runtime/schedule_state')); a=ap.parse_args()
    run_at=dt.datetime.fromisoformat(a.run_at.replace('Z','+00:00')).astimezone(dt.timezone.utc); run_id=hashlib.sha256(f'{a.schedule_id}:{run_at.isoformat()}'.encode()).hexdigest()[:16]
    p=ScheduleStateStore(a.state_dir).write_run_record({'run_id':run_id,'schedule_id':a.schedule_id,'run_at':run_at.isoformat(),'executed_at':dt.datetime.now(dt.timezone.utc).isoformat(),'status':'manually_marked'})
    print(json.dumps({'run_id':run_id,'path':str(p)},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
