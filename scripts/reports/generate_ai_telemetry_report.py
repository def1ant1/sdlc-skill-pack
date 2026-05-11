#!/usr/bin/env python3
"""Generate AI telemetry summaries and replay narratives from run-history artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

TRACE_ORDER = ["planner", "router", "memory", "tool", "evaluator", "governor"]


def _load_events(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        if isinstance(payload.get("events"), list):
            return [item for item in payload["events"] if isinstance(item, dict)]
        return [payload]
    return []


def _normalize_stage(event: dict[str, Any]) -> str:
    stage = str(event.get("trace_stage") or event.get("stage") or "unknown").lower()
    return stage if stage in TRACE_ORDER else "unknown"


def build_replay_narrative(events: list[dict[str, Any]]) -> list[str]:
    grouped: dict[str, list[dict[str, Any]]] = {stage: [] for stage in TRACE_ORDER}
    for event in events:
        stage = _normalize_stage(event)
        if stage in grouped:
            grouped[stage].append(event)

    narrative: list[str] = []
    for stage in TRACE_ORDER:
        stage_events = grouped[stage]
        if not stage_events:
            narrative.append(f"- {stage}: no events captured")
            continue
        errors = sum(1 for e in stage_events if str(e.get("status", "")).lower() == "error")
        warns = sum(1 for e in stage_events if str(e.get("status", "")).lower() == "warn")
        sample = stage_events[-1].get("message") or stage_events[-1].get("event_type") or "completed"
        narrative.append(
            f"- {stage}: {len(stage_events)} event(s), warn={warns}, error={errors}; latest={sample}"
        )
    return narrative


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="runtime/workflow_history", help="JSON file or directory")
    parser.add_argument("--output", default="reports/ai_telemetry_report.md", help="markdown output path")
    args = parser.parse_args()

    input_path = Path(args.input)
    files = [input_path] if input_path.is_file() else sorted(input_path.glob("*.json"))

    all_events: list[dict[str, Any]] = []
    for file_path in files:
        all_events.extend(_load_events(file_path))

    narrative = build_replay_narrative(all_events)
    stage_counts = {stage: sum(1 for e in all_events if _normalize_stage(e) == stage) for stage in TRACE_ORDER}

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "\n".join(
            [
                "# AI Telemetry Report",
                "",
                f"Runs scanned: {len(files)}",
                f"Total telemetry events: {len(all_events)}",
                "",
                "## Stage coverage",
                *[f"- {stage}: {count}" for stage, count in stage_counts.items()],
                "",
                "## Replay narrative",
                *narrative,
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
