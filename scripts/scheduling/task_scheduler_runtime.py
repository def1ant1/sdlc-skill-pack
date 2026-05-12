from __future__ import annotations
import datetime as dt, json
from pathlib import Path

def _task_path(task_id:str, task_dir:Path)->Path:
    return task_dir / f"{task_id}.json"

def create_task_from_schedule_run(run:dict, schedule:dict, task_dir:Path)->Path|None:
    if not schedule.get("generate_task", False):
        return None
    task_dir.mkdir(parents=True, exist_ok=True)
    task_id=f"task-{run['schedule_id']}-{run['run_id']}"
    payload={
      "task_id":task_id,
      "title":f"Recurring run follow-up: {run['schedule_id']}",
      "origin":"workflow",
      "source_ref":run["run_id"],
      "dependencies":[],
      "acceptance_criteria":["Review recurring run output","Close or escalate findings"],
      "status":"open",
      "assignee":{"type":"role","id":schedule.get("owner","ops")},
      "created_at":dt.datetime.now(dt.timezone.utc).isoformat()
    }
    p=_task_path(task_id, task_dir); p.write_text(json.dumps(payload, indent=2, sort_keys=True)+"\n")
    return p

def set_schedule_state(registry:Path, schedule_id:str, enabled:bool|None=None, archived:bool|None=None)->bool:
    import yaml
    payload=yaml.safe_load(registry.read_text()) or {}
    changed=False
    for s in payload.get("schedules",[]):
      if s.get("schedule_id")==schedule_id:
        if enabled is not None: s["enabled"]=enabled; changed=True
        if archived is not None: s["archived"]=archived; changed=True
    if changed:
      registry.write_text(yaml.safe_dump(payload, sort_keys=False))
    return changed
