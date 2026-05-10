#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_CATEGORIES = {"runtime", "business"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path to JSON file containing an event or list of events")
    args = parser.parse_args()

    path = Path(args.input)
    payload = json.loads(path.read_text(encoding="utf-8"))
    events = payload if isinstance(payload, list) else [payload]

    errors: list[str] = []
    for idx, event in enumerate(events):
        category = str(event.get("event_category", "")).lower()
        if category in REQUIRED_CATEGORIES and not str(event.get("correlation_id", "")).strip():
            errors.append(f"event[{idx}] missing correlation_id for category '{category}'")

    if errors:
        print("\n".join(errors))
        return 1

    print("Telemetry events valid: correlation_id present for runtime/business events.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
