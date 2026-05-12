#!/usr/bin/env python3
"""Conversation → living plan pipeline.

Builds a human-readable structured plan first, then supports living-plan edits and
approval workflow needed by downstream execution converters.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass
class PlanStep:
    id: str
    title: str
    description: str
    priority: int
    approvals_required: list[str] = field(default_factory=lambda: ["human"])
    status: str = "pending"


@dataclass
class PlanPhase:
    id: str
    title: str
    objective: str
    tasks: list[PlanStep]
    approvals_required: bool = True
    collapsed: bool = False


@dataclass
class ConfidenceAnnotation:
    field: str
    value: str
    source: str  # explicit_user | inferred_assumption
    confidence: str = "medium"


@dataclass
class PlannerInputs:
    conversation_summary: str = ""
    constraints: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    desired_outputs: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    preferences: list[str] = field(default_factory=list)
    prior_decisions: list[str] = field(default_factory=list)


@dataclass
class LivingPlan:
    id: str
    title: str
    source_conversation: str
    objectives: list[str]
    assumptions: list[str]
    risks: list[str]
    dependencies: list[str]
    required_skills: list[str]
    phases: list[PlanPhase]
    planner_inputs: PlannerInputs = field(default_factory=PlannerInputs)
    confidence_annotations: list[ConfidenceAnnotation] = field(default_factory=list)
    unanswered_questions: list[str] = field(default_factory=list)
    version: int = 1
    history: list[dict[str, Any]] = field(default_factory=list)


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _extract_bullets(text: str) -> list[str]:
    bullets = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith(("- ", "* ")):
            bullets.append(line[2:].strip())
    return bullets


def _extract_answered_questions(state: dict[str, Any] | None) -> set[str]:
    if not state:
        return set()
    answered = set(state.get("resolved_questions", []) or [])
    orchestrator = state.get("orchestrator", {}) if isinstance(state, dict) else {}
    answered.update(orchestrator.get("resolved_questions", []) or [])
    curated = state.get("curated_memory", {}) if isinstance(state, dict) else {}
    for row in curated.get("qa_pairs", []) or []:
        q = str(row.get("question", "")).strip().lower()
        if q:
            answered.add(q)
    return {q.strip().lower() for q in answered if q}


def conversation_to_plan(conversation: str, *, title: str = "Conversation-Derived Plan", orchestrator_state: dict[str, Any] | None = None) -> LivingPlan:
    bullets = _extract_bullets(conversation)
    objectives = bullets or [s.strip() for s in re.split(r"[.!?]", conversation) if s.strip()][:3]
    assumptions = ["Timeline is negotiable based on approvals.", "Required repositories and credentials are available."]
    risks = ["Unclear scope can cause rework.", "Approvals may block timeline if delayed."]
    dependencies = ["Plan review and per-step approvals", "Artifact schema compatibility"]
    required_skills = ["requirements-engineering", "workflow-optimization-loop", "checkpoint-management"]

    answered = _extract_answered_questions(orchestrator_state)
    candidate_questions = ["what is the success metric", "what deadline applies", "which systems are in scope"]
    unanswered = [q for q in candidate_questions if q not in answered]

    phases: list[PlanPhase] = []
    for pidx, objective in enumerate(objectives, start=1):
        phase_id = f"phase-{pidx}"
        steps = [
            PlanStep(id=f"{phase_id}-task-1", title="Define scope", description=f"Clarify objective: {objective}", priority=1),
            PlanStep(id=f"{phase_id}-task-2", title="Design approach", description="Draft actionable implementation steps.", priority=2),
            PlanStep(id=f"{phase_id}-task-3", title="Review and approve", description="Secure explicit step-level approvals.", priority=3),
        ]
        phases.append(PlanPhase(id=phase_id, title=f"Phase {pidx}", objective=objective, tasks=steps))

    planner_inputs = PlannerInputs(
        conversation_summary=" ".join(objectives)[:300],
        constraints=["respect approval gates", "preserve workflow schema compatibility"],
        assumptions=assumptions,
        desired_outputs=["approved workflow", "task breakdown", "decision log"],
        entities=["objective", "phase", "task", "approval"],
        preferences=["draft-first", "deterministic outputs"],
        prior_decisions=list(answered),
    )
    confidence_annotations = [
        ConfidenceAnnotation(field="objectives", value="derived from conversation bullets/sentences", source="explicit_user", confidence="high"),
        ConfidenceAnnotation(field="assumptions", value="timeline and repo access defaults", source="inferred_assumption", confidence="medium"),
    ]

    plan = LivingPlan(
        id=f"plan-{int(dt.datetime.now().timestamp())}",
        title=title,
        source_conversation=conversation.strip(),
        objectives=objectives,
        assumptions=assumptions,
        risks=risks,
        dependencies=dependencies,
        required_skills=required_skills,
        phases=phases,
        planner_inputs=planner_inputs,
        confidence_annotations=confidence_annotations,
        unanswered_questions=unanswered,
    )
    plan.history.append({"version": 1, "timestamp": _utc_now(), "action": "created"})
    return plan


def _record_version(plan: LivingPlan, action: str, details: dict[str, Any]) -> LivingPlan:
    plan.version += 1
    plan.history.append({"version": plan.version, "timestamp": _utc_now(), "action": action, "details": details})
    return plan


def collapse_expand_section(plan: LivingPlan, phase_id: str, collapsed: bool) -> LivingPlan:
    for phase in plan.phases:
        if phase.id == phase_id:
            phase.collapsed = collapsed
            return _record_version(plan, "collapse_toggle", {"phase_id": phase_id, "collapsed": collapsed})
    raise ValueError(f"phase not found: {phase_id}")


def reorder_priorities(plan: LivingPlan, phase_id: str, ordered_task_ids: list[str]) -> LivingPlan:
    for phase in plan.phases:
        if phase.id == phase_id:
            idx = {tid: i + 1 for i, tid in enumerate(ordered_task_ids)}
            for task in phase.tasks:
                if task.id in idx:
                    task.priority = idx[task.id]
            phase.tasks.sort(key=lambda t: t.priority)
            return _record_version(plan, "reorder_priorities", {"phase_id": phase_id, "task_ids": ordered_task_ids})
    raise ValueError(f"phase not found: {phase_id}")


def edit_assumptions(plan: LivingPlan, assumptions: list[str]) -> LivingPlan:
    plan.assumptions = assumptions
    plan.planner_inputs.assumptions = assumptions
    return _record_version(plan, "edit_assumptions", {"assumptions": assumptions})


def approve_step(plan: LivingPlan, step_id: str, approver: str) -> LivingPlan:
    for phase in plan.phases:
        for step in phase.tasks:
            if step.id == step_id:
                step.status = "approved"
                step.approvals_required = [a for a in step.approvals_required if a != approver]
                return _record_version(plan, "approve_step", {"step_id": step_id, "approver": approver})
    raise ValueError(f"step not found: {step_id}")


def version_diff_history(plan: LivingPlan, from_version: int, to_version: int) -> dict[str, Any]:
    changes = [h for h in plan.history if from_version < h["version"] <= to_version]
    return {"from_version": from_version, "to_version": to_version, "changes": changes}


def _to_dict(plan: LivingPlan) -> dict[str, Any]:
    payload = asdict(plan)
    payload["phases"] = [
        {**asdict(p), "tasks": [asdict(t) for t in p.tasks]}
        for p in plan.phases
    ]
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a living plan from conversation text")
    parser.add_argument("--conversation", help="Conversation text input")
    parser.add_argument("--stdin", action="store_true", help="Read conversation text from stdin")
    parser.add_argument("--title", default="Conversation-Derived Plan")
    parser.add_argument("--orchestrator-state", type=Path, help="Optional JSON state used to avoid re-asking answered questions")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    conversation = args.conversation or ""
    if args.stdin or not conversation:
        import sys
        conversation = sys.stdin.read().strip()

    orchestrator_state = None
    if args.orchestrator_state:
        orchestrator_state = json.loads(args.orchestrator_state.read_text(encoding="utf-8"))

    plan = conversation_to_plan(conversation, title=args.title, orchestrator_state=orchestrator_state)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(_to_dict(plan), indent=2) + "\n", encoding="utf-8")
    print(json.dumps(_to_dict(plan), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
