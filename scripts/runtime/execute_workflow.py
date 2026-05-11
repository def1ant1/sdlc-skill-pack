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

import hashlib
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
from error_envelope import build_error_envelope



SIDE_EFFECT_READ_ONLY = "read-only"
SIDE_EFFECT_SIMULATED_MUTATION = "simulated-mutation"
SIDE_EFFECT_REAL_MUTATION = "real-mutation"


def classify_side_effect(step: dict, dry_run: bool) -> str:
    """Classify step side effects for governance and audit logs."""
    declared = step.get("side_effect")
    if declared in {SIDE_EFFECT_READ_ONLY, SIDE_EFFECT_SIMULATED_MUTATION, SIDE_EFFECT_REAL_MUTATION}:
        if dry_run and declared == SIDE_EFFECT_REAL_MUTATION:
            return SIDE_EFFECT_SIMULATED_MUTATION
        return declared

    gate = str(step.get("gate_before_next", "")).lower()
    skill = str(step.get("skill", "")).lower()
    mutating_hints = ("deploy", "provision", "rotate", "migrate", "release", "write", "update", "delete", "devsecops", "security", "incident")
    if any(h in gate for h in mutating_hints) or any(h in skill for h in mutating_hints):
        return SIDE_EFFECT_SIMULATED_MUTATION if dry_run else SIDE_EFFECT_REAL_MUTATION
    return SIDE_EFFECT_READ_ONLY


def _stable_timestamp(dry_run: bool) -> str:
    if dry_run:
        return "1970-01-01T00:00:00Z"
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _deterministic_run_id(plan: dict, dry_run: bool) -> str:
    if not dry_run:
        return f"RUN-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    canonical = json.dumps(plan, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]
    return f"DRYRUN-{digest}"
EXECUTION_MODE = os.environ.get("EXECUTION_MODE", "local")
TEMPORAL_HOST = os.environ.get("TEMPORAL_HOST", "localhost:7233")
TEMPORAL_NAMESPACE = os.environ.get("TEMPORAL_NAMESPACE", "apotheon-dev")
TEMPORAL_TASK_QUEUE = os.environ.get("TEMPORAL_TASK_QUEUE", "apotheon-sdlc")
TEMPORAL_TIMEOUT_HOURS = int(os.environ.get("TEMPORAL_TIMEOUT_HOURS", "4"))


# ---------------------------------------------------------------------------

WORKFLOW_HISTORY_DIR = Path(__file__).resolve().parents[2] / "runtime" / "workflow_history"


def _persist_execution_artifact(execution_log: dict, history_dir: Path = WORKFLOW_HISTORY_DIR) -> None:
    history_dir.mkdir(parents=True, exist_ok=True)
    run_id = execution_log.get("run_id")
    if not run_id:
        raise ValueError("execution artifact missing run_id")
    if not execution_log.get("started_at"):
        raise ValueError("execution artifact missing started_at")
    if execution_log.get("status") != "running" and not execution_log.get("completed_at"):
        raise ValueError("terminal execution artifact missing completed_at")
    out = history_dir / f"{run_id}.json"
    out.write_text(json.dumps(execution_log, indent=2, sort_keys=True)+"\n")

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
    run_id = _deterministic_run_id(plan, dry_run)
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
        "started_at": _stable_timestamp(dry_run),
        "completed_at": None,
    }

    cm = _make_context_manager(run_id, objective) if not dry_run else None
    context_packet = cm.load() if cm else {"objective": objective, "phase": "", "decisions": [], "constraints": [], "artifacts": [], "risks": [], "next_action": ""}
    prior_outputs: list[str] = []

    prev_dry_run_env = os.environ.get("APOTHEON_DRY_RUN")
    if dry_run:
        os.environ["APOTHEON_DRY_RUN"] = "1"

    try:
        for step in steps:
            skill_name = step.get("skill", "")
            step_num = step.get("step", 0)
            gate = step.get("gate_before_next")
            step_record = {"step": step_num, "skill": skill_name, "status": "skipped" if dry_run else "running", "output": None, "error": None, "duration_ms": 0, "hitl_required": False, "side_effect_classification": classify_side_effect(step, dry_run)}

            if dry_run:
                step_record["status"] = "dry_run"
                execution_log["steps"].append(step_record)
                continue

            additional_context_parts: list[str] = []
            if prior_outputs:
                additional_context_parts.extend(f"[Prior step output]\n{o[:2000]}" for o in prior_outputs[-2:])
            if cm:
                for obs in cm.retrieve_relevant(f"{objective} {skill_name}", top_k=3):
                    preview = obs.get("payload", {}).get("output_preview", "")
                    obs_skill = obs.get("payload", {}).get("skill", "")
                    if preview and obs_skill != skill_name:
                        additional_context_parts.append(f"[Memory: {obs_skill}]\n{preview[:800]}")

            context_packet["phase"] = step.get("phase", skill_name)
            inp = SkillActivityInput(skill_name=skill_name, objective=objective, context_packet=context_packet, additional_context="\n\n---\n\n".join(additional_context_parts))
            t0 = time.perf_counter()
            try:
                result = run_skill_activity(inp)
            except Exception as exc:
                duration_ms = int((time.perf_counter() - t0) * 1000)
                envelope = build_error_envelope(correlation_id=run_id, workflow_run_id=run_id, skill=skill_name or "runtime", step=step_num, category="runtime", retryable=False, user_action_required=True, message="Workflow step failed.", technical_detail=str(exc), root_cause_hint="Skill execution exception", remediation="Inspect step error details and rerun with --resume once corrected.", source_exception=repr(exc))
                step_record.update({"status": "error", "error": json.dumps(envelope, sort_keys=True), "duration_ms": duration_ms})
                execution_log.update({"status": "failed", "failed_at_step": step_num})
                execution_log["steps"].append(step_record)
                if cm:
                    cm.finalize("failed")
                break

            duration_ms = int((time.perf_counter() - t0) * 1000)
            step_record.update({"status": "completed" if result.success else "failed", "output": result.output[:500] if result.output else None, "error": result.error or None, "duration_ms": duration_ms, "hitl_required": result.requires_hitl})
            if result.requires_hitl:
                step_record["status"] = "pending_hitl"
                execution_log.update({"status": "paused_for_hitl", "paused_at_step": step_num})
                execution_log["steps"].append(step_record)
                if cm:
                    cm.save_context(context_packet)
                break

            if not result.success:
                execution_log.update({"status": "failed", "failed_at_step": step_num})
                execution_log["steps"].append(step_record)
                if cm:
                    cm.finalize("failed")
                break

            prior_outputs.append(result.output)
            context_packet["artifacts"].append(f"{skill_name}_output")
            if cm:
                cm.save_step(step=step_num, skill=skill_name, output=result.output)
                cm.save_context(context_packet)
            if gate:
                step_record["gate_reached"] = gate
            execution_log["steps"].append(step_record)
        else:
            if not dry_run:
                execution_log["status"] = "completed"
                if cm:
                    cm.finalize("completed")

        execution_log["completed_at"] = _stable_timestamp(dry_run)
        if dry_run:
            execution_log["status"] = "dry_run"
    finally:
        if dry_run:
            if prev_dry_run_env is None:
                os.environ.pop("APOTHEON_DRY_RUN", None)
            else:
                os.environ["APOTHEON_DRY_RUN"] = prev_dry_run_env

    _record_workflow(execution_log["status"], "local", sum(s.get("duration_ms", 0) for s in execution_log["steps"]) / 1000.0)
    _persist_execution_artifact(execution_log)
    return execution_log


# ---------------------------------------------------------------------------
# Temporal execution (requires temporalio package)
# ---------------------------------------------------------------------------

async def _submit_temporal(plan: dict) -> dict:
    """Async implementation: connect to Temporal, start ApotheonWorkflow, await result."""
    from datetime import timedelta
    from temporalio.client import Client

    run_id = _deterministic_run_id(plan, False)

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

        if isinstance(result.get("steps"), list):
            result["steps"] = sorted(result["steps"], key=lambda r: r.get("step", 0))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result.get("status") in ("completed", "dry_run") else 1
    except Exception as exc:
        logger.error("Workflow execution failed: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
