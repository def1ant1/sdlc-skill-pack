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

    # Temporal mode (requires temporal_worker.py running)
    python scripts/runtime/execute_workflow.py --mode temporal --plan workflow_plan.json

Environment variables:
    EXECUTION_MODE       local | temporal (default: local)
    TEMPORAL_HOST        Temporal server host (default: localhost:7233)
    TEMPORAL_NAMESPACE   Temporal namespace (default: apotheon-dev)
    TEMPORAL_TASK_QUEUE  Task queue name (default: apotheon-sdlc)
    TEMPORAL_TIMEOUT_HOURS  Hours to wait for Temporal workflow (default: 4)
    ANTHROPIC_API_KEY    Required for local mode skill execution
    QDRANT_URL           Qdrant URL for context persistence (default: http://localhost:6333)
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
TEMPORAL_TIMEOUT_HOURS = int(os.environ.get("TEMPORAL_TIMEOUT_HOURS", "4"))


# ---------------------------------------------------------------------------
# Context manager (graceful — Qdrant may not be running)
# ---------------------------------------------------------------------------

def _make_context_manager(run_id: str, objective: str):
    """Return a ContextManager instance, or None if unavailable."""
    try:
        from context_manager import ContextManager
        return ContextManager(run_id=run_id, objective=objective)
    except Exception as exc:
        logger.debug("ContextManager unavailable — memory persistence disabled: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Telemetry (graceful — emits to log file, fails silently)
# ---------------------------------------------------------------------------

_TELEMETRY_ROOT = Path(os.environ.get("TELEMETRY_LOG", "")).parent if os.environ.get("TELEMETRY_LOG") else None
_TELEMETRY_LOG = os.environ.get("TELEMETRY_LOG", "telemetry.log.yaml")

_TELEMETRY_PATH: list[str] = [str(Path(__file__).parent.parent / "telemetry")]
_APP_PATH = str(Path(__file__).parent.parent.parent)


def _record_workflow(status: str, mode: str, duration_s: float) -> None:
    """Record workflow run Prometheus metric. No-ops if app/ not available."""
    try:
        if _APP_PATH not in sys.path:
            sys.path.insert(0, _APP_PATH)
        from app.observability.metrics import record_workflow_run
        record_workflow_run(status=status, mode=mode, duration_s=duration_s)
    except Exception:
        pass


def _emit_telemetry(
    run_id: str,
    phase: str,
    gate_result: str,
    duration_ms: int,
    *,
    tokens_used: int = 0,
    artifacts: list[str] | None = None,
    quality_score: float | None = None,
) -> None:
    """Emit a telemetry event. No-ops silently if the telemetry module is unavailable."""
    try:
        import sys as _sys
        for _p in _TELEMETRY_PATH:
            if _p not in _sys.path:
                _sys.path.insert(0, _p)
        from record_telemetry_event import append_to_log, build_event_record

        event: dict = {
            "workflow_id": run_id,
            "phase": phase,
            "gate_result": gate_result,
            "tokens_used": tokens_used,
            "duration_ms": duration_ms,
            "artifacts_produced": artifacts or [],
        }
        if quality_score is not None:
            event["quality_score"] = quality_score

        record = build_event_record(event)
        append_to_log(record, _TELEMETRY_LOG)
        if record.get("anomalies"):
            for a in record["anomalies"]:
                logger.warning(
                    "Telemetry anomaly [%s] %s=%s (threshold=%s)",
                    a["severity"].upper(), a["metric"], a["value"], a["threshold"],
                )
    except Exception as exc:
        logger.debug("Telemetry emit skipped: %s", exc)


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

    # Initialise context — restore from Qdrant snapshot if a prior run exists
    cm = _make_context_manager(run_id, objective) if not dry_run else None
    context_packet = cm.load() if cm else {
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

        # Build additional context: recent step outputs + semantically relevant observations
        additional_context_parts: list[str] = []

        if prior_outputs:
            recent = prior_outputs[-2:]  # last 2 outputs for chain continuity
            additional_context_parts.extend(
                f"[Prior step output]\n{o[:2000]}" for o in recent
            )

        if cm:
            # Fetch semantically relevant observations from past runs
            query = f"{objective} {skill_name}"
            relevant = cm.retrieve_relevant(query, top_k=3)
            for obs in relevant:
                preview = obs.get("payload", {}).get("output_preview", "")
                obs_skill = obs.get("payload", {}).get("skill", "")
                if preview and obs_skill != skill_name:
                    additional_context_parts.append(
                        f"[Memory: {obs_skill}]\n{preview[:800]}"
                    )

        additional_context = "\n\n---\n\n".join(additional_context_parts)
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
            step_record["output"] = result.output[:500] if result.output else None
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
                _emit_telemetry(
                    run_id=run_id,
                    phase=skill_name,
                    gate_result="PASS_WITH_WARNINGS",
                    duration_ms=duration_ms,
                )
                if cm:
                    cm.save_context(context_packet)
                break

            if result.success:
                prior_outputs.append(result.output)
                context_packet["artifacts"].append(f"{skill_name}_output")
                if cm:
                    cm.save_step(step=step_num, skill=skill_name, output=result.output)
                    cm.save_context(context_packet)
                _emit_telemetry(
                    run_id=run_id,
                    phase=skill_name,
                    gate_result="PASS",
                    duration_ms=duration_ms,
                    artifacts=[f"{skill_name}_output"],
                )
            else:
                logger.error("Step %d (%s) failed: %s", step_num, skill_name, result.error)
                _emit_telemetry(
                    run_id=run_id,
                    phase=skill_name,
                    gate_result="FAIL",
                    duration_ms=duration_ms,
                )
                execution_log["status"] = "failed"
                execution_log["failed_at_step"] = step_num
                execution_log["steps"].append(step_record)
                if cm:
                    cm.finalize("failed")
                break

        except Exception as exc:
            duration_ms = int((time.perf_counter() - t0) * 1000)
            step_record["status"] = "error"
            step_record["error"] = str(exc)
            step_record["duration_ms"] = duration_ms
            logger.error("Step %d (%s) raised exception: %s", step_num, skill_name, exc, exc_info=True)
            _emit_telemetry(run_id=run_id, phase=skill_name, gate_result="FAIL", duration_ms=duration_ms)
            execution_log["status"] = "failed"
            execution_log["failed_at_step"] = step_num
            execution_log["steps"].append(step_record)
            if cm:
                cm.finalize("failed")
            break

        # Gate check (informational in local mode — no blocking)
        if gate:
            logger.info("Gate reached: %s", gate)
            step_record["gate_reached"] = gate

        execution_log["steps"].append(step_record)

    else:
        # All steps completed without a break
        if not dry_run:
            execution_log["status"] = "completed"
            if cm:
                cm.finalize("completed")

    execution_log["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if dry_run:
        execution_log["status"] = "dry_run"

    # Record workflow-level Prometheus metric
    total_duration_s = sum(s.get("duration_ms", 0) for s in execution_log["steps"]) / 1000.0
    _record_workflow(execution_log["status"], "local", total_duration_s)

    return execution_log


# ---------------------------------------------------------------------------
# Temporal execution (requires temporalio package)
# ---------------------------------------------------------------------------

async def _submit_temporal(plan: dict) -> dict:
    """Async implementation: connect to Temporal, start ApotheonWorkflow, await result."""
    from datetime import timedelta
    from temporalio.client import Client

    run_id = f"RUN-{int(time.time())}-{uuid.uuid4().hex[:8]}"

    logger.info(
        "Connecting to Temporal at %s (namespace=%s, queue=%s)",
        TEMPORAL_HOST, TEMPORAL_NAMESPACE, TEMPORAL_TASK_QUEUE,
    )
    client = await Client.connect(TEMPORAL_HOST, namespace=TEMPORAL_NAMESPACE)

    logger.info("Starting ApotheonWorkflow: %s", run_id)
    handle = await client.start_workflow(
        "ApotheonWorkflow",
        plan,
        id=run_id,
        task_queue=TEMPORAL_TASK_QUEUE,
        execution_timeout=timedelta(hours=TEMPORAL_TIMEOUT_HOURS),
    )

    logger.info("Workflow submitted (id=%s). Waiting for result...", run_id)
    result: dict = await handle.result()

    # Ensure run_id from submission matches (the workflow generates its own internal ID)
    if "run_id" not in result:
        result["run_id"] = run_id
    result["temporal_workflow_id"] = run_id

    return result


def execute_temporal(plan: dict) -> dict:
    """Submit workflow plan to Temporal for durable execution."""
    try:
        import temporalio  # noqa: F401
    except ImportError:
        raise RuntimeError(
            "temporalio package not installed. Run: pip install 'apotheon[temporal]'\n"
            "Or use EXECUTION_MODE=local for in-process execution."
        )

    import asyncio
    logger.info(
        "Temporal mode — requires temporal_worker.py to be running against %s",
        TEMPORAL_HOST,
    )
    return asyncio.run(_submit_temporal(plan))


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