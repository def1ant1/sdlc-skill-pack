#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def _load_health_results(root: Path) -> list[dict]:
    proc = subprocess.run(["python", "scripts/connectors/health_check.py", "--json"], cwd=root, text=True, capture_output=True, check=False)
    if not proc.stdout.strip():
        return []
    return json.loads(proc.stdout)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    results = _load_health_results(root)
    by_status = Counter(r.get("status", "UNKNOWN") for r in results)
    by_failure = Counter(r.get("failure_type", "none") for r in results if r.get("status") != "OK")
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total": len(results),
            "ok": by_status.get("OK", 0),
            "degraded": by_status.get("DEGRADED", 0),
            "unreachable": by_status.get("UNREACHABLE", 0),
            "by_failure_type": dict(by_failure),
        },
        "connectors": results,
        "dashboard_export": {
            "connector_health": {
                "healthy": by_status.get("OK", 0),
                "degraded": by_status.get("DEGRADED", 0),
                "down": by_status.get("UNREACHABLE", 0),
                "failure_breakdown": dict(by_failure),
            }
        },
    }
    (reports / "connector_health_report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Connector Health Report",
        "",
        f"Generated: `{payload['generated_at']}`",
        "",
        "## Summary",
        f"- Total connectors: **{payload['summary']['total']}**",
        f"- OK: **{payload['summary']['ok']}**",
        f"- Degraded: **{payload['summary']['degraded']}**",
        f"- Unreachable: **{payload['summary']['unreachable']}**",
        "",
        "## Failure breakdown",
    ]
    if by_failure:
        for k,v in sorted(by_failure.items()):
            lines.append(f"- {k}: **{v}**")
    else:
        lines.append("- none")
    lines += ["", "## Connector details", "", "| Connector | Status | Failure Type | Latency |", "|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['connector']} | {r['status']} | {r.get('failure_type') or '-'} | {str(r.get('latency_ms') or '-')} |")
    (reports / "connector_health_report.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
