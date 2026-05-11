#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate rate limit report")
    ap.add_argument("--usage", type=Path, default=Path("runtime/rate_limit_usage.json"))
    ap.add_argument("--out", type=Path, default=Path("reports/rate_limit_report.json"))
    args = ap.parse_args()
    usage = json.loads(args.usage.read_text()) if args.usage.exists() else {"connectors": []}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(usage, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"written": str(args.out), "connectors": len(usage.get('connectors', []))}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
