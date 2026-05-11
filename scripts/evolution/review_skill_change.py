#!/usr/bin/env python3
"""Enforce explicit human approval before any proposed improvement can proceed."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proposal", required=True)
    parser.add_argument("--approved-by", default="")
    args = parser.parse_args()

    proposal = json.loads(Path(args.proposal).read_text(encoding="utf-8"))
    high_risk = [p for p in proposal.get("proposals", []) if p.get("risk_level") == "high"]

    approved_by = args.approved_by.strip()
    if not approved_by:
        print("BLOCKED: explicit human approval is required (--approved-by).")
        return 2

    decision = {
        "approved": True,
        "approved_by": approved_by,
        "high_risk_items": len(high_risk),
        "auto_apply": False,
        "auto_merge": False,
        "manual_review_required": True,
    }
    print(json.dumps(decision, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
