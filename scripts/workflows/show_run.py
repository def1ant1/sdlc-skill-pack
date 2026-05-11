#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_RUNS_ROOT = Path("runtime/workflow_runs")


def _resolve_record(run_id: str, runs_root: Path) -> Path:
    record = runs_root / run_id / "run_record.json"
    if not record.exists():
        raise FileNotFoundError(f"Run record not found: {record}")
    return record


def main() -> int:
    ap = argparse.ArgumentParser(description="Show one local workflow run record.")
    ap.add_argument("run_id")
    ap.add_argument("--runs-root", type=Path, default=DEFAULT_RUNS_ROOT)
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args()

    payload = json.loads(_resolve_record(a.run_id, a.runs_root).read_text(encoding="utf-8"))
    if a.summary:
        summary = {
            "run_id": payload.get("run_id"),
            "status": payload.get("status"),
            "objective": payload.get("objective"),
            "started_at": payload.get("started_at"),
            "completed_at": payload.get("completed_at"),
            "steps": len(payload.get("steps", [])),
            "storage": payload.get("storage", {}),
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
