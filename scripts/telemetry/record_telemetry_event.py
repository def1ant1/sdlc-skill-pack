#!/usr/bin/env python3
"""
Record a telemetry event from a workflow phase transition.

Reads a telemetry event payload (JSON/YAML from stdin or --file),
validates it against the schema, appends it to the telemetry log,
and emits any anomalies detected.

Usage:
    echo '{"workflow_id": "WP-20260506-001", "phase": "architecture", ...}' | python record_telemetry_event.py
    python record_telemetry_event.py --file event.json --log telemetry.log.yaml
    python record_telemetry_event.py --file event.json --check-anomalies
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Anomaly thresholds (mirrors references/anomaly-thresholds.md)
# ---------------------------------------------------------------------------

THRESHOLDS = {
    "token_efficiency":       {"warn": 0.55, "alert": 0.40, "direction": "below"},
    "output_consistency":     {"warn": 85.0, "alert": 70.0, "direction": "below"},
    "hallucination_rate":     {"warn": 8.0,  "alert": 15.0, "direction": "above"},
    "tool_call_success_rate": {"warn": 90.0, "alert": 80.0, "direction": "below"},
    "artifact_completeness":  {"warn": 90.0, "alert": 75.0, "direction": "below"},
    "budget_utilization":     {"warn": 80.0, "alert": 95.0, "direction": "above"},
    "quality_score":          {"warn": 60.0, "alert": 40.0, "direction": "below"},
}

REQUIRED_FIELDS = [
    "workflow_id", "phase", "gate_result", "tokens_used",
]


def _load_input(path: Optional[str]) -> dict:
    """Load event payload from file or stdin."""
    if path:
        raw = Path(path).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()

    raw = raw.strip()
    # Try JSON first
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    # Try YAML
    try:
        import yaml  # type: ignore
        return yaml.safe_load(raw)
    except ImportError:
        pass
    raise ValueError("Input is not valid JSON or YAML (and PyYAML is not installed)")


def validate_event(event: dict) -> list[str]:
    """Validate required fields. Returns list of error messages."""
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in event:
            errors.append(f"missing required field: {field}")
    if event.get("gate_result") not in {
        "PASS", "FAIL", "PASS_WITH_WARNINGS", "NOT_EVALUATED", "SKIPPED", None
    }:
        errors.append(f"invalid gate_result: {event.get('gate_result')}")
    return errors


def detect_anomalies(event: dict) -> list[dict]:
    """Check event metrics against thresholds. Returns list of anomaly records."""
    anomalies = []
    for metric, cfg in THRESHOLDS.items():
        value = event.get(metric)
        if value is None:
            continue
        direction = cfg["direction"]
        if direction == "below":
            if value < cfg["alert"]:
                severity = "alert"
            elif value < cfg["warn"]:
                severity = "warn"
            else:
                continue
        else:  # above
            if value > cfg["alert"]:
                severity = "alert"
            elif value > cfg["warn"]:
                severity = "warn"
            else:
                continue

        anomalies.append({
            "metric": metric,
            "value": value,
            "threshold": cfg["alert"] if severity == "alert" else cfg["warn"],
            "severity": severity,
        })
    return anomalies


def build_event_record(event: dict) -> dict:
    """Build a complete telemetry event record with generated fields."""
    now = datetime.now(timezone.utc).isoformat()
    phase = event.get("phase", "unknown")

    # Simple sequential ID (not collision-safe for concurrent writes)
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    event_id = f"TEL-{date_str}-{abs(hash(now + phase)) % 1000:03d}"

    # Budget utilization
    tokens_used = event.get("tokens_used", 0)
    budget_total = event.get("budget_total")
    budget_utilization = None
    if budget_total and budget_total > 0:
        budget_utilization = round((tokens_used / budget_total) * 100, 1)

    record = {
        "event_id": event_id,
        "timestamp": now,
        "workflow_id": event.get("workflow_id"),
        "phase": phase,
        "gate_result": event.get("gate_result", "NOT_EVALUATED"),
        "tokens_used": tokens_used,
        "budget_total": budget_total,
        "budget_utilization": budget_utilization,
        "budget_remaining": event.get("budget_remaining"),
        "duration_ms": event.get("duration_ms"),
        "artifacts_produced": event.get("artifacts_produced", []),
        "quality_score": event.get("quality_score"),
        "token_efficiency": event.get("token_efficiency"),
        "output_consistency": event.get("output_consistency"),
        "hallucination_rate": event.get("hallucination_rate"),
        "tool_call_success_rate": event.get("tool_call_success_rate"),
        "artifact_completeness": event.get("artifact_completeness"),
        "anomalies": detect_anomalies({**event, "budget_utilization": budget_utilization}),
    }
    # Strip None values for cleaner output
    return {k: v for k, v in record.items() if v is not None}


def append_to_log(record: dict, log_path: str) -> None:
    """Append the event record to the YAML telemetry log."""
    log_file = Path(log_path)
    try:
        import yaml  # type: ignore
        existing = ""
        if log_file.exists():
            existing = log_file.read_text(encoding="utf-8")
        entry = yaml.dump([record], default_flow_style=False, allow_unicode=True)
        # Remove the leading "- " list marker and reformat as a document separator
        with log_file.open("a", encoding="utf-8") as f:
            f.write("---\n")
            f.write(yaml.dump(record, default_flow_style=False, allow_unicode=True))
    except ImportError:
        # Fallback: append as JSON lines
        with log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Record a telemetry event from a workflow phase.")
    parser.add_argument("--file", help="Path to event JSON/YAML file (default: stdin)")
    parser.add_argument("--log", default="telemetry.log.yaml", help="Telemetry log file to append to")
    parser.add_argument("--check-anomalies", action="store_true",
                        help="Print anomalies and exit non-zero if any alerts found")
    parser.add_argument("--dry-run", action="store_true", help="Print record without writing to log")
    args = parser.parse_args()

    event = _load_input(args.file)

    errors = validate_event(event)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    record = build_event_record(event)

    if args.dry_run:
        print(json.dumps(record, indent=2))
        return

    append_to_log(record, args.log)
    print(f"Recorded: {record['event_id']} (phase={record['phase']}, gate={record['gate_result']})")

    if record.get("anomalies"):
        for anomaly in record["anomalies"]:
            print(f"  [{anomaly['severity'].upper()}] {anomaly['metric']}={anomaly['value']} "
                  f"(threshold={anomaly['threshold']})", file=sys.stderr)

    if args.check_anomalies:
        has_alerts = any(a["severity"] == "alert" for a in record.get("anomalies", []))
        sys.exit(1 if has_alerts else 0)


if __name__ == "__main__":
    main()