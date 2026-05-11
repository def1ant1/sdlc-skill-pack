#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from zoneinfo import ZoneInfo
import yaml
REGISTRY_PATH=Path(__file__).resolve().parents[2]/'schedules'/'registry.yaml'
WORKFLOW_REGISTRY=Path(__file__).resolve().parents[2]/'workflows'/'registry'/'workflow-plans.yaml'

def validate_schedule(s:dict,known:set[str])->list[str]:
    sid=s.get('schedule_id','<unknown>'); e=[]; m=s.get('mode')
    if m not in {'cron','interval','manual','event'}: e.append(f'{sid}: unsupported mode {m}')
    if m=='cron' and len(str(s.get('cron','')).split())!=5: e.append(f'{sid}: invalid cron')
    if m=='interval' and int(s.get('interval_minutes',0))<=0: e.append(f'{sid}: invalid interval_minutes')
    if m=='event' and not s.get('event_trigger'): e.append(f'{sid}: missing event_trigger')
    if m=='manual' and not s.get('manual_reason',''): e.append(f'{sid}: missing manual_reason')
    try: ZoneInfo(s.get('timezone','UTC'))
    except Exception: e.append(f"{sid}: invalid timezone {s.get('timezone')}")
    if s.get('planner_target') and s.get('planner_target') not in known: e.append(f'{sid}: unknown planner_target')
    if s.get('concurrency','forbid') not in {'forbid','replace','allow'}: e.append(f'{sid}: invalid concurrency')
    if s.get('misfire_policy','skip') not in {'skip','run_once','catch_up'}: e.append(f'{sid}: invalid misfire_policy')
    return e

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--registry',type=Path,default=REGISTRY_PATH); ap.add_argument('--workflow-registry',type=Path,default=WORKFLOW_REGISTRY); a=ap.parse_args()
    schedules=(yaml.safe_load(a.registry.read_text()) or {}).get('schedules',[])
    wf=(yaml.safe_load(a.workflow_registry.read_text()) or {})
    known={p.get('planner') for p in wf.get('workflow_plans',[]) if p.get('planner')}
    errs=[x for s in schedules for x in validate_schedule(s,known)]
    print(json.dumps({'valid':not errs,'errors':errs},indent=2)); return 1 if errs else 0
if __name__=='__main__': raise SystemExit(main())
