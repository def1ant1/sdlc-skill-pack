#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate_source(doc: dict, file: Path) -> list[str]:
    errors: list[str] = []

    legal = doc.get("legal", {})
    robots = doc.get("robots", {})
    tos = doc.get("terms_of_service", {})
    throttle = doc.get("throttling", {})

    if not legal.get("review_approved", False):
        errors.append("legal.review_approved must be true")
    if not robots.get("allow_scraping", False):
        errors.append("robots.allow_scraping must be true")
    if not tos.get("allow_automation", False):
        errors.append("terms_of_service.allow_automation must be true")

    rpm = throttle.get("max_requests_per_minute", 0)
    burst = throttle.get("burst_limit", 0)
    cooldown = throttle.get("cooldown_seconds", -1)
    if not isinstance(rpm, int) or rpm < 1:
        errors.append("throttling.max_requests_per_minute must be an integer >= 1")
    if not isinstance(burst, int) or burst < 1:
        errors.append("throttling.burst_limit must be an integer >= 1")
    if not isinstance(cooldown, int) or cooldown < 0:
        errors.append("throttling.cooldown_seconds must be an integer >= 0")

    network = doc.get("network", {})
    if network.get("allow_residential_proxy", False):
        errors.append("network.allow_residential_proxy must be false")

    lineage = doc.get("lineage", {})
    for required in ("dataset", "entity_type", "run_id_prefix", "retention_days"):
        if required not in lineage:
            errors.append(f"lineage.{required} is required")

    return [f"{file}: {error}" for error in errors]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate marketplace source policy compliance")
    parser.add_argument("--path", type=Path, default=Path("runtime/marketplace_sources"))
    args = parser.parse_args()

    files = sorted(args.path.glob("*.json")) if args.path.exists() else []
    violations: list[str] = []

    for source_file in files:
        doc = json.loads(source_file.read_text())
        violations.extend(validate_source(doc, source_file))

    if violations:
        print("non-compliant marketplace sources detected:")
        print("\n".join(violations))
        return 1

    print(f"validated {len(files)} marketplace source definition(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
