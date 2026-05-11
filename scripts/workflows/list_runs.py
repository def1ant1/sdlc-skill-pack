#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_RUNS_ROOT = Path("runtime/workflow_runs")


def main() -> int:
    ap = argparse.ArgumentParser(description="List local workflow runs.")
    ap.add_argument("--runs-root", type=Path, default=DEFAULT_RUNS_ROOT)
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    records = []
    for record in sorted(a.runs_root.glob("*/run_record.json"), reverse=True):
        payload = json.loads(record.read_text(encoding="utf-8"))
        records.append({
            "run_id": payload.get("run_id"),
            "status": payload.get("status"),
            "mode": payload.get("mode"),
            "started_at": payload.get("started_at"),
            "completed_at": payload.get("completed_at"),
            "path": str(record),
        })
    records = records[: max(0, a.limit)]

    if a.json:
        print(json.dumps(records, indent=2, sort_keys=True))
    else:
        for r in records:
            print(f"{r['run_id']}\t{r['status']}\t{r['started_at']}\t{r['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
