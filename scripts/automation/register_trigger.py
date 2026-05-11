#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Register an automation trigger")
    parser.add_argument("--trigger", type=Path, required=True, help="Trigger JSON payload")
    parser.add_argument("--registry", type=Path, default=Path("runtime/automation/trigger_registry.json"))
    parser.add_argument("--schema", type=Path, default=Path("schemas/automation-trigger.schema.json"))
    args = parser.parse_args()

    payload = json.loads(args.trigger.read_text(encoding="utf-8"))
    if args.schema.exists():
        try:
            import jsonschema
            schema = json.loads(args.schema.read_text(encoding="utf-8"))
            jsonschema.validate(instance=payload, schema=schema)
        except ImportError:
            pass

    registry = []
    if args.registry.exists():
        registry = json.loads(args.registry.read_text(encoding="utf-8"))
    registry = [t for t in registry if t.get("trigger_id") != payload.get("trigger_id")]
    registry.append(payload)
    args.registry.parent.mkdir(parents=True, exist_ok=True)
    args.registry.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Registered trigger {payload.get('trigger_id')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
