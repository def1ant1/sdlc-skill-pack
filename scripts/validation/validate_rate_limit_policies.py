#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path


def validate_policy(doc: dict) -> list[str]:
    errors = []
    for required in ["connector_id", "requests_per_minute", "degrade_to_cached_at", "degrade_to_read_only_at"]:
        if required not in doc:
            errors.append(f"missing required field: {required}")
    if "degrade_to_cached_at" in doc and "degrade_to_read_only_at" in doc:
        if doc["degrade_to_cached_at"] < doc["degrade_to_read_only_at"]:
            errors.append("degrade_to_cached_at must be >= degrade_to_read_only_at")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate rate limit policies")
    ap.add_argument("--path", type=Path, default=Path("runtime/rate_limit_policies"))
    args = ap.parse_args()
    files = sorted(args.path.glob("*.json")) if args.path.exists() else []
    all_errors = []
    for file in files:
        doc = json.loads(file.read_text())
        errs = validate_policy(doc)
        for e in errs:
            all_errors.append(f"{file}: {e}")
    if all_errors:
        print("\n".join(all_errors))
        return 1
    print(f"validated {len(files)} rate-limit policies")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
