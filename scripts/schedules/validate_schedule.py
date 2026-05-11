#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from zoneinfo import ZoneInfo
import yaml

REGISTRY_PATH = Path(__file__).resolve().parents[2] / 'schedules' / 'registry.yaml'
WORKFLOW_REGISTRY = Path(__file__).resolve().parents[2] / 'workflows' / 'registry' / 'workflow-plans.yaml'

def validate_schedule(schedule: dict, known_workflows: set[str]) -> list[str]:
    sid = schedule.get('schedule_id','<unknown>'); errs=[]; mode=schedule.get('mode')
    if mode not in {'cron','interval','event'}: errs.append(f'{sid}: unsupported mode {mode}')
    if mode=='cron' and len(str(schedule.get('cron','')).split())!=5: errs.append(f'{sid}: invalid cron')
    if mode=='interval' and int(schedule.get('interval_minutes',0))<=0: errs.append(f'{sid}: invalid interval_minutes')
    if mode=='event' and not schedule.get('event_trigger'): errs.append(f'{sid}: missing event_trigger')
    try: ZoneInfo(schedule.get('timezone','UTC'))
    except Exception: errs.append(f"{sid}: invalid timezone {schedule.get('timezone')}")
    if schedule.get('planner_target') not in known_workflows: errs.append(f'{sid}: unknown planner_target')
    if schedule.get('concurrency','forbid') not in {'forbid','replace','allow'}: errs.append(f'{sid}: invalid concurrency')
    if schedule.get('misfire_policy','skip') not in {'skip','run_once','catch_up'}: errs.append(f'{sid}: invalid misfire_policy')
    return errs

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--registry',type=Path,default=REGISTRY_PATH); ap.add_argument('--workflow-registry',type=Path,default=WORKFLOW_REGISTRY); a=ap.parse_args()
    schedules=(yaml.safe_load(a.registry.read_text()) or {}).get('schedules',[])
    wf=(yaml.safe_load(a.workflow_registry.read_text()) or {})
    known={p.get('planner') for p in wf.get('workflow_plans',[])}
    errors=[e for s in schedules for e in validate_schedule(s,known)]
    print(json.dumps({'valid':not errors,'errors':errors}, indent=2)); return 1 if errors else 0

if __name__=='__main__': raise SystemExit(main())
