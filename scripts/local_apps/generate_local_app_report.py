from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _status(flag: bool) -> str:
    return "PASS" if flag else "FAIL"


def render_markdown(report: dict[str, Any]) -> str:
    lines = ["# Local App Health Report", ""]
    env = report["env_validation"]
    lines += [f"## Env Validation: {_status(env['passed'])}"]
    for miss in env["missing"]:
        lines.append(f"- ❌ `{miss['variable']}`: {miss['remediation']}")

    lines += ["", "## Service Health"]
    for svc in report["service_health"]:
        lines.append(
            f"- **{svc['name']}**: container_running={svc['container_running']}, "
            f"container_health={svc['container_health']}, api_usable={svc['api_usable']} ({svc['api_message']})"
        )

    for key in ["startup_dependency_order", "port_conflicts", "volume_existence"]:
        section = report[key]
        lines += ["", f"## {key.replace('_', ' ').title()}: {_status(section['passed'])}"]
        detail_key = "warnings" if "warnings" in section else "conflicts" if "conflicts" in section else "missing"
        if section[detail_key]:
            for item in section[detail_key]:
                lines.append(f"- ⚠️ {item}")

    backup = report["backup_readiness"]
    lines += ["", f"## Backup Readiness: {_status(backup['ready'])}", f"- {backup['remediation']}"]

    lines += ["", "## Upgrade/Migration Warnings"]
    warnings = report.get("upgrade_migration_warnings", [])
    if warnings:
        lines += [f"- ⚠️ {w}" for w in warnings]
    else:
        lines.append("- none")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-md", type=Path)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    report = json.loads(args.input.read_text())
    md = render_markdown(report)
    if args.output_md:
        args.output_md.write_text(md)
    if args.output_json:
        args.output_json.write_text(json.dumps(report, indent=2) + "\n")
    print(md)


if __name__ == "__main__":
    main()
