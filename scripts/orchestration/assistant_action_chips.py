#!/usr/bin/env python3
"""Generate explainable assistant action chips and auditable action events."""
from __future__ import annotations

import argparse
import datetime as dt
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

CHIP_SET = [
    "create_plan",
    "convert_to_workflow",
    "break_into_tasks",
    "save_as_skill",
    "schedule_recurrence",
    "add_to_knowledge",
    "run_dry_run",
    "request_approval",
    "show_dependencies",
    "show_risks",
    "generate_report",
    "confirm_plan",
    "adjust_plan_seo_audit",
    "adjust_plan_technical",
    "adjust_plan_content",
    "adjust_plan_performance",
]


@dataclass
class ActionChip:
    key: str
    label: str
    explain_why: str
    reversible: dict[str, Any]
    payload: dict[str, Any]



def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_action_chips(response_context: dict[str, Any], active_artifacts: list[dict[str, Any]]) -> list[ActionChip]:
    artifact_types = {a.get("type") for a in active_artifacts}
    has_plan = "plan" in artifact_types
    has_workflow = "workflow" in artifact_types
    has_tasks = "task" in artifact_types

    chips: list[ActionChip] = []
    def add(key: str, label: str, why: str, payload: dict[str, Any] | None = None) -> None:
        chips.append(ActionChip(
            key=key,
            label=label,
            explain_why=why,
            reversible={"supported": True, "operations": ["undo", "cancel", "edit_before_execute"]},
            payload=payload or {},
        ))

    if not has_plan:
        add("create_plan", "Create plan", "No active plan artifact was found in this conversation context.")
    if has_plan and not has_workflow:
        add("convert_to_workflow", "Convert to workflow", "A plan exists but no workflow artifact exists yet.")
    if has_plan and not has_tasks:
        add("break_into_tasks", "Break into tasks", "Plan phases are present but task artifacts are missing.")

    add("save_as_skill", "Save as skill", "Response contains reusable patterns that can be persisted as a skill template.")
    add("schedule_recurrence", "Schedule recurrence", "Request appears repeatable and can be converted into a schedule.")
    add("add_to_knowledge", "Add to knowledge", "Response includes reusable decisions worth durable memory capture.")

    if has_workflow:
        add("run_dry_run", "Run dry-run", "Workflow artifact exists and can be safely simulated before side effects.")
    if response_context.get("governance", {}).get("require_approval"):
        add("request_approval", "Request approval", "Governance policy indicates approval is required before execution.")

    add("show_dependencies", "Show dependencies", "Dependency visibility reduces execution ordering mistakes.")
    add("show_risks", "Show risks", "Risk visibility improves user control before execution.")
    add("generate_report", "Generate report", "Execution/readiness status can be summarized for sharing.")
    add("confirm_plan", "Confirm plan", "Plan can be confirmed before execution begins.", {"status": "confirm"})
    add("adjust_plan_seo_audit", "SEO audit", "Focuses plan on SEO analysis and prioritization.", {"chip": "seo_audit"})
    add("adjust_plan_technical", "Technical", "Focuses plan on technical implementation details.", {"chip": "technical"})
    add("adjust_plan_content", "Content", "Focuses plan on content strategy and production.", {"chip": "content"})
    add("adjust_plan_performance", "Performance", "Focuses plan on performance optimization steps.", {"chip": "performance"})

    return [c for c in chips if c.key in CHIP_SET]


def record_chip_action_event(*, chip_key: str, action: str, conversation_id: str, message_id: str, artifact_id: str | None = None) -> dict[str, Any]:
    return {
        "event_id": f"assistant-action-event-{int(dt.datetime.now().timestamp())}",
        "event_type": "assistant_action_chip_triggered",
        "timestamp": _utc_now(),
        "conversation_id": conversation_id,
        "message_id": message_id,
        "chip_key": chip_key,
        "action": action,
        "artifact_id": artifact_id,
        "audit": {"actor": "assistant", "traceable": True},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate assistant action chips")
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    context = json.loads(args.context.read_text(encoding="utf-8"))
    artifacts = json.loads(args.artifacts.read_text(encoding="utf-8"))
    chips = [asdict(c) for c in generate_action_chips(context, artifacts)]
    payload = {"chips": chips, "generated_at": _utc_now()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
