#!/usr/bin/env python3
"""
execute_workflow.py — Execute a workflow plan produced by plan_workflow.py.

Reads a workflow plan JSON (from plan_workflow.py output) and executes each
skill in dependency order, passing context between steps.

In production this submits to Temporal; in local/dev mode it runs steps
sequentially in-process (no Temporal required).

Usage:
    # Generate plan then execute
    python scripts/orchestration/plan_workflow.py "Build a secure REST API" | \
        python scripts/runtime/execute_workflow.py

    # Execute a saved plan
    python scripts/runtime/execute_workflow.py --plan workflow_plan.json

    # Dry run (print steps without executing)
    python scripts/runtime/execute_workflow.py --plan workflow_plan.json --dry-run

Environment variables:
    EXECUTION_MODE       local | temporal (default: local)
    TEMPORAL_HOST        Temporal server host (default: localhost:7233)
    TEMPORAL_NAMESPACE   Temporal namespace (default: apotheon-dev)
    TEMPORAL_TASK_QUEUE  Task queue name (default: apotheon-sdlc)
    ANTHROPIC_API_KEY    Required for local mode skill execution
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
import uuid
from pathlib import Path

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("execute_workflow")

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))
from skill_activity import SkillActivityInput, run_skill_activity  # noqa: E402

EXECUTION_MODE = os.environ.get("EXECUTION_MODE", "local")
TEMPORAL_HOST = os.environ.get("TEMPORAL_HOST", "localhost:7233")
TEMPORAL_NAMESPACE = os.environ.get("TEMPORAL_NAMESPACE", "apotheon-dev")
TEMPORAL_TASK_QUEUE = os.environ.get("TEMPORAL_TASK_QUEUE", "apotheon-sdlc")


# ---------------------------------------------------------------------------
# Local execution engine
# ---------------------------------------------------------------------------

def execute_local(plan: dict, dry_run: bool = False) -> dict:
    """Execute a workflow plan locally, step by step."""
    run_id = f"RUN-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    objective = plan.get("objective", "")
    steps = plan.get("skill_chain", [])

    logger.info("Starting local workflow execution: %s (%d steps)", run_id, len(steps))

    execution_log = {
        "run_id": run_id,
        "mode": "local",
        "objective": objective,
        "plan_id": plan.get("plan_id", ""),
        "total_steps": len(steps),
        "steps": [],
        "status": "running",
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "completed_at": None,
    }

    # Build context packet from plan
    context_packet = {
        "objective": objective,
        "phase": "",
        "decisions": [],
        "constraints": [],
        "artifacts": [],
        "risks": [],
        "next_action": "",
    }

    prior_outputs: list[str] = []

    for step in steps:
        skill_name = step.get("skill", "")
        step_num = step.get("step", 0)
        gate = step.get("gate_before_next")

        logger.info("Step %d/%d: %s", step_num, len(steps), skill_name)

        step_record: dict = {
            "step": step_num,
            "skill": skill_name,
            "status": "skipped" if dry_run else "running",
            "output": None,
            "error": None,
            "duration_ms": 0,
            "hitl_required": False,
        }

        if dry_run:
            logger.info("[DRY RUN] Would execute skill: %s", skill_name)
            step_record["status"] = "dry_run"
            execution_log["steps"].append(step_record)
            continue

        # Build additional context from prior step outputs
        additional_context = ""
        if prior_outputs:
            recent = prior_outputs[-2:]  # last 2 outputs for context
            additional_context = "\n\n---\n\n".join(
                f"[Prior step output]\n{o[:2000]}" for o in recent
            )

        context_packet["phase"] = step.get("phase", skill_name)

        inp = SkillActivityInput(
            skill_name=skill_name,
            objective=objective,
            context_packet=context_packet,
            additional_context=additional_context,
        )

        t0 = time.perf_counter()
        try:
            result = run_skill_activity(inp)
            duration_ms = int((time.perf_counter() - t0) * 1000)

            step_record["status"] = "completed" if result.success else "failed"
            step_record["output"] = result.output[:500] if result.output else None  # truncate for log
            step_record["error"] = result.error or None
            step_record["duration_ms"] = duration_ms
            step_record["hitl_required"] = result.requires_hitl

            if result.requires_hitl:
                logger.warning(
                    "Step %d (%s) requires HITL approval: %s",
                    step_num, skill_name, result.hitl_reason,
                )
                step_record["status"] = "pending_hitl"
                execution_log["steps"].append(step_record)
                execution_log["status"] = "paused_for_hitl"
                execution_log["paused_at_step"] = step_num
                break

            if result.success:
                prior_outputs.append(result.output)
                # Add any decisions/artifacts extracted from output to context
                context_packet["artifacts"].append(f"{skill_name}_output")
            else:
                logger.error("Step %d (%s) failed: %s", step_num, skill_name, result.error)
                execution_log["status"] = "failed"
                execution_log["failed_at_step"] = step_num
                execution_log["steps"].append(step_record)
                break

        except Exception as exc:
            duration_ms = int((time.perf_counter() - t0) * 1000)
            step_record["status"] = "error"
            step_record["error"] = str(exc)
            step_record["duration_ms"] = duration_ms
            logger.error("Step %d (%s) raised exception: %s", step_num, skill_name, exc, exc_info=True)
            execution_log["status"] = "failed"
            execution_log["failed_at_step"] = step_num
            execution_log["steps"].append(step_record)
            break

        # Gate check (informational in local mode — no blocking)
        if gate:
            logger.info("Gate reached: %s", gate)
            step_record["gate_reached"] = gate

        execution_log["steps"].append(step_record)

    else:
        # All steps completed
        if not dry_run:
            execution_log["status"] = "completed"

    execution_log["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if dry_run:
        execution_log["status"] = "dry_run"

    return execution_log


# ---------------------------------------------------------------------------
# Temporal execution (requires temporalio package)
# ---------------------------------------------------------------------------

def execute_temporal(plan: dict) -> dict:
    """Submit workflow plan to Temporal for durable execution."""
    try:
        import temporalio  # noqa: F401
    except ImportError:
        raise RuntimeError(
            "temporalio package not installed. Run: pip install temporalio\n"
            "Or use EXECUTION_MODE=local for in-process execution."
        )

    logger.warning(
        "Temporal execution requires temporal_worker.py to be running. "
        "Submitting workflow to %s namespace=%s",
        TEMPORAL_HOST, TEMPORAL_NAMESPACE,
    )
    # Full Temporal client implementation requires async context.
    # See scripts/runtime/temporal_worker.py for the worker and workflow definitions.
    raise NotImplementedError(
        "Temporal submission requires async runner. "
        "Use: python -m asyncio scripts/runtime/temporal_worker.py"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Execute an Apotheon workflow plan")
    parser.add_argument("--plan", help="Path to workflow plan JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Print steps without executing")
    parser.add_argument("--mode", choices=["local", "temporal"], default=EXECUTION_MODE)
    args = parser.parse_args()

    if args.plan:
        plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    else:
        try:
            plan = json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            logger.error("Invalid workflow plan JSON: %s", exc)
            return 1

    if not plan.get("skill_chain"):
        logger.error("Workflow plan has no skill_chain — nothing to execute")
        return 1

    try:
        if args.mode == "temporal":
            result = execute_temporal(plan)
        else:
            result = execute_local(plan, dry_run=args.dry_run)

        print(json.dumps(result, indent=2))
        return 0 if result.get("status") in ("completed", "dry_run") else 1
    except Exception as exc:
        logger.error("Workflow execution failed: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())