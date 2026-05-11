#!/usr/bin/env python3
"""
temporal_worker.py — Temporal worker and workflow definitions for Apotheon.

Registers skill activities and the ApotheonWorkflow workflow with Temporal.
Requires the 'temporalio' package: pip install temporalio

Usage:
    python scripts/runtime/temporal_worker.py

Environment variables:
    TEMPORAL_HOST        Temporal server (default: localhost:7233)
    TEMPORAL_NAMESPACE   Temporal namespace (default: apotheon-dev)
    TEMPORAL_TASK_QUEUE  Task queue (default: apotheon-sdlc)
    ANTHROPIC_API_KEY    Required for skill activity execution
    MAX_CONCURRENT_ACTIVITIES  (default: 10)
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
from datetime import timedelta
from pathlib import Path

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("temporal_worker")

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))

TEMPORAL_HOST = os.environ.get("TEMPORAL_HOST", "localhost:7233")
TEMPORAL_NAMESPACE = os.environ.get("TEMPORAL_NAMESPACE", "apotheon-dev")
TEMPORAL_TASK_QUEUE = os.environ.get("TEMPORAL_TASK_QUEUE", "apotheon-sdlc")
MAX_CONCURRENT = int(os.environ.get("MAX_CONCURRENT_ACTIVITIES", "10"))
DEFAULT_STEP_TIMEOUT_SECONDS = int(os.environ.get("MAX_STEP_RUNTIME", "600"))


# ---------------------------------------------------------------------------
# Activity definitions (wrapped for Temporal)
# ---------------------------------------------------------------------------

def _get_temporalio():
    """Import temporalio or raise a clear error."""
    try:
        import temporalio
        return temporalio
    except ImportError:
        raise RuntimeError(
            "temporalio package not installed.\n"
            "Install: pip install temporalio\n"
            "Docs: https://docs.temporal.io/develop/python"
        )


def build_activities():
    """Return Temporal activity-decorated versions of skill_activity functions."""
    _get_temporalio()
    from temporalio import activity
    from skill_activity import SkillActivityInput, SkillActivityOutput, run_skill_activity

    @activity.defn(name="run_skill")
    async def run_skill_temporal(inp_dict: dict) -> dict:
        """Temporal activity: execute one skill and return its output dict."""
        inp = SkillActivityInput.from_dict(inp_dict)
        # Run in executor to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        result: SkillActivityOutput = await loop.run_in_executor(None, run_skill_activity, inp)
        return result.to_dict()

    return run_skill_temporal


# ---------------------------------------------------------------------------
# Workflow definition
# ---------------------------------------------------------------------------

def build_workflow():
    """Return the ApotheonWorkflow class with Temporal decorators."""
    _get_temporalio()
    from temporalio import workflow
    from temporalio.common import RetryPolicy

    @workflow.defn(name="ApotheonWorkflow")
    class ApotheonWorkflow:
        """
        Durable workflow that executes an Apotheon skill chain.

        Input: workflow plan dict (same schema as plan_workflow.py output)
        Output: execution log dict (same schema as execute_workflow.py output)
        """

        @workflow.run
        async def run(self, plan: dict) -> dict:
            import time
            import uuid

            run_id = f"RUN-{int(time.time())}-{uuid.uuid4().hex[:8]}"
            objective = plan.get("objective", "")
            steps = plan.get("skill_chain", [])

            workflow.logger.info("Workflow started: %s (%d steps)", run_id, len(steps))

            execution_log = {
                "run_id": run_id,
                "mode": "temporal",
                "objective": objective,
                "plan_id": plan.get("plan_id", ""),
                "total_steps": len(steps),
                "steps": [],
                "status": "running",
                "started_at": "",
                "completed_at": None,
            }

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

            retry_policy = RetryPolicy(
                initial_interval=timedelta(seconds=1),
                backoff_coefficient=2.0,
                maximum_interval=timedelta(seconds=60),
                maximum_attempts=3,
            )

            for step in steps:
                skill_name = step.get("skill", "")
                step_num = step.get("step", 0)
                context_packet["phase"] = step.get("phase", skill_name)

                additional_context = ""
                if prior_outputs:
                    recent = prior_outputs[-2:]
                    additional_context = "\n\n---\n\n".join(
                        f"[Prior step output]\n{o[:2000]}" for o in recent
                    )

                inp_dict = {
                    "skill_name": skill_name,
                    "objective": objective,
                    "context_packet": context_packet,
                    "additional_context": additional_context,
                }

                step_record: dict = {
                    "step": step_num,
                    "skill": skill_name,
                    "status": "running",
                    "output": None,
                    "error": None,
                    "duration_ms": 0,
                    "hitl_required": False,
                }

                try:
                    result_dict = await workflow.execute_activity(
                        "run_skill",
                        inp_dict,
                        start_to_close_timeout=timedelta(seconds=DEFAULT_STEP_TIMEOUT_SECONDS),
                        retry_policy=retry_policy,
                    )

                    step_record["status"] = "completed" if result_dict["success"] else "failed"
                    step_record["output"] = (result_dict.get("output") or "")[:500]
                    step_record["error"] = result_dict.get("error") or None
                    step_record["hitl_required"] = result_dict.get("requires_hitl", False)

                    if result_dict.get("requires_hitl"):
                        step_record["status"] = "pending_hitl"
                        execution_log["steps"].append(step_record)
                        execution_log["status"] = "paused_for_hitl"
                        execution_log["paused_at_step"] = step_num
                        return execution_log

                    if result_dict["success"]:
                        prior_outputs.append(result_dict.get("output", ""))
                        context_packet["artifacts"].append(f"{skill_name}_output")
                    else:
                        execution_log["status"] = "failed"
                        execution_log["failed_at_step"] = step_num
                        execution_log["steps"].append(step_record)
                        return execution_log

                except Exception as exc:
                    step_record["status"] = "error"
                    step_record["error"] = str(exc)
                    execution_log["status"] = "failed"
                    execution_log["failed_at_step"] = step_num
                    execution_log["steps"].append(step_record)
                    return execution_log

                execution_log["steps"].append(step_record)

            execution_log["status"] = "completed"
            return execution_log

    return ApotheonWorkflow


# ---------------------------------------------------------------------------
# Worker bootstrap
# ---------------------------------------------------------------------------

async def run_worker() -> None:
    _get_temporalio()
    from temporalio.client import Client
    from temporalio.worker import Worker

    run_skill_activity_fn = build_activities()
    ApotheonWorkflow = build_workflow()

    logger.info(
        "Connecting to Temporal at %s (namespace=%s, queue=%s)",
        TEMPORAL_HOST, TEMPORAL_NAMESPACE, TEMPORAL_TASK_QUEUE,
    )
    client = await Client.connect(TEMPORAL_HOST, namespace=TEMPORAL_NAMESPACE)

    worker = Worker(
        client,
        task_queue=TEMPORAL_TASK_QUEUE,
        workflows=[ApotheonWorkflow],
        activities=[run_skill_activity_fn],
        max_concurrent_activities=MAX_CONCURRENT,
    )
    logger.info("Worker started — polling task queue '%s'", TEMPORAL_TASK_QUEUE)
    await worker.run()


def main() -> None:
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
