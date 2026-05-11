from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compose-file", type=Path, default=Path("local_apps/docker-compose.local-apps.yml"))
    parser.add_argument("--mapping-file", type=Path, default=Path("local_apps/mappings/local_app_categories.yaml"))
    args = parser.parse_args()

    compose = yaml.safe_load(args.compose_file.read_text())
    mappings = yaml.safe_load(args.mapping_file.read_text())
    services = sorted((compose.get("services") or {}).keys())
    out = {
        "services": services,
        "canonical_categories": mappings.get("canonical_categories", {}),
        "priority_apps": mappings.get("priority_apps", []),
        "mapping_coverage": mappings.get("mapping_coverage", {}),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
