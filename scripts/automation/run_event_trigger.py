#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def _run_governance(trigger: dict, repo_root: Path) -> dict:
    req = {
        "skill_path": "core/trigger-engine",
        "requested_actions": trigger.get("governance", {}).get("requested_actions", []),
        "autonomous_mode": trigger.get("governance", {}).get("autonomous_mode", False),
        "approval_granted": trigger.get("dry_run", True),
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        f.write(json.dumps(req))
        req_path = Path(f.name)
    out = subprocess.run([
        "python", "scripts/governance/enforce_runtime_policy.py", "--request", str(req_path)
    ], cwd=repo_root, capture_output=True, text=True)
    try:
        req_path.unlink(missing_ok=True)
    except Exception:
        pass
    decision = {}
    try:
        decision = json.loads(out.stdout.splitlines()[0])
    except Exception:
        decision = {"status": "deny" if out.returncode else "allow", "raw": out.stdout}
    decision["exit_code"] = out.returncode
    return decision


def main() -> int:
    parser = argparse.ArgumentParser(description="Run triggers for an event type")
    parser.add_argument("--event-type", required=True)
    parser.add_argument("--event-payload", type=Path, help="Optional event JSON payload")
    parser.add_argument("--registry", type=Path, default=Path("runtime/automation/trigger_registry.json"))
    parser.add_argument("--history", type=Path, default=Path("runtime/automation/trigger_history.jsonl"))
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    event_payload = json.loads(args.event_payload.read_text(encoding="utf-8")) if args.event_payload else {}
    registry = json.loads(args.registry.read_text(encoding="utf-8")) if args.registry.exists() else []
    matches = [t for t in registry if t.get("event_type") == args.event_type and t.get("enabled", True)]

    args.history.parent.mkdir(parents=True, exist_ok=True)
    launches = 0
    for trigger in matches:
        decision = _run_governance(trigger, repo_root)
        status = "blocked_by_governance"
        run_rc = None
        if decision.get("status") == "allow":
            cmd = ["python", "scripts/runtime/execute_workflow.py", "--plan", trigger["workflow_plan"]]
            if trigger.get("dry_run", True):
                cmd.append("--dry-run")
            run = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
            run_rc = run.returncode
            status = "launched" if run.returncode == 0 else "launch_failed"
            launches += 1 if run.returncode == 0 else 0
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": args.event_type,
            "event_payload": event_payload,
            "trigger_id": trigger.get("trigger_id"),
            "workflow_plan": trigger.get("workflow_plan"),
            "dry_run": trigger.get("dry_run", True),
            "governance_status": decision.get("status"),
            "execution_status": status,
            "execution_exit_code": run_rc,
        }
        with args.history.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")
        print(json.dumps(record))

    print(f"Processed {len(matches)} triggers; successful launches={launches}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
