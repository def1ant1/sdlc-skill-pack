#!/usr/bin/env python3
"""
hitl_handler.py — Human-in-the-loop approval routing for Apotheon workflows.

When a workflow step flags requires_hitl=True, this module:
  1. Posts an approval request to a Slack channel (#apotheon-approvals)
  2. Polls for a ✅ (approve) or ❌ (reject) reaction from an authorized approver
  3. Sends the corresponding Temporal signal to resume or cancel the workflow

Can also be used standalone to approve/reject a workflow by run ID.

Usage:
    # Send HITL notification and wait for approval
    python scripts/runtime/hitl_handler.py notify <run-id> --skill <skill> --reason "<reason>"

    # Approve a paused workflow
    python scripts/runtime/hitl_handler.py approve <run-id>

    # Reject a paused workflow
    python scripts/runtime/hitl_handler.py reject <run-id> --reason "Budget not approved"

Environment variables:
    TEMPORAL_HOST            Temporal gRPC address (default: localhost:7233)
    TEMPORAL_NAMESPACE       Temporal namespace (default: apotheon-dev)
    TEMPORAL_TASK_QUEUE      Task queue (default: apotheon-sdlc)
    HITL_SLACK_CHANNEL       Slack channel for approvals (default: #apotheon-approvals)
    HITL_POLL_INTERVAL       Seconds between reaction polls (default: 30)
    HITL_TIMEOUT_SECONDS     Max wait for approval (default: 86400 = 24h)
    HITL_AUTHORIZED_USERS    Comma-separated Slack user IDs who can approve
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path

logger = logging.getLogger("hitl_handler")

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE.parent))

TEMPORAL_HOST = os.environ.get("TEMPORAL_HOST", "localhost:7233")
TEMPORAL_NAMESPACE = os.environ.get("TEMPORAL_NAMESPACE", "apotheon-dev")
TEMPORAL_TASK_QUEUE = os.environ.get("TEMPORAL_TASK_QUEUE", "apotheon-sdlc")
HITL_SLACK_CHANNEL = os.environ.get("HITL_SLACK_CHANNEL", "#apotheon-approvals")
HITL_POLL_INTERVAL = int(os.environ.get("HITL_POLL_INTERVAL", "30"))
HITL_TIMEOUT_SECONDS = int(os.environ.get("HITL_TIMEOUT_SECONDS", str(86400)))
HITL_AUTHORIZED_USERS = {
    u.strip()
    for u in os.environ.get("HITL_AUTHORIZED_USERS", "").split(",")
    if u.strip()
}

APPROVE_EMOJI = "white_check_mark"
REJECT_EMOJI = "x"


# ---------------------------------------------------------------------------
# Temporal signal senders
# ---------------------------------------------------------------------------

def _get_temporal_client():
    try:
        from temporalio.client import Client
        import asyncio
        return asyncio.get_event_loop().run_until_complete(
            Client.connect(TEMPORAL_HOST, namespace=TEMPORAL_NAMESPACE)
        )
    except ImportError:
        raise RuntimeError("temporalio not installed — run: pip install temporalio")


def approve_workflow(run_id: str, approver: str = "operator", justification: str = "") -> None:
    """Send hitl_approved signal to a paused Temporal workflow."""
    import asyncio

    async def _send():
        from temporalio.client import Client
        client = await Client.connect(TEMPORAL_HOST, namespace=TEMPORAL_NAMESPACE)
        handle = client.get_workflow_handle(run_id)
        await handle.signal("hitl_approved", {"approver": approver, "justification": justification})
        logger.info("Sent hitl_approved signal to workflow %s", run_id)

    asyncio.run(_send())


def reject_workflow(run_id: str, approver: str = "operator", reason: str = "") -> None:
    """Send hitl_rejected signal to a paused Temporal workflow."""
    import asyncio

    async def _send():
        from temporalio.client import Client
        client = await Client.connect(TEMPORAL_HOST, namespace=TEMPORAL_NAMESPACE)
        handle = client.get_workflow_handle(run_id)
        await handle.signal("hitl_rejected", {"approver": approver, "reason": reason})
        logger.info("Sent hitl_rejected signal to workflow %s", run_id)

    asyncio.run(_send())


# ---------------------------------------------------------------------------
# Slack notification + reaction polling
# ---------------------------------------------------------------------------

def _slack_connector():
    sys.path.insert(0, str(_HERE.parent / "connectors"))
    from slack_connector import SlackConnector
    return SlackConnector()


def _build_approval_blocks(run_id: str, skill: str, reason: str, step: int) -> list[dict]:
    return [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Apotheon HITL Approval Required"},
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Run ID:*\n`{run_id}`"},
                {"type": "mrkdwn", "text": f"*Skill:*\n`{skill}`"},
                {"type": "mrkdwn", "text": f"*Step:*\n{step}"},
                {"type": "mrkdwn", "text": f"*Gate Reason:*\n{reason}"},
            ],
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"React with :white_check_mark: to *approve* or :x: to *reject*.\n"
                        f"Authorized approvers only. Timeout: 24h.",
            },
        },
    ]


def notify_and_wait(
    run_id: str,
    skill: str,
    reason: str,
    step: int = 0,
) -> tuple[bool, str]:
    """
    Post HITL approval request to Slack and poll for reaction.

    Returns:
        (approved: bool, approver: str)

    Raises:
        TimeoutError if no reaction within HITL_TIMEOUT_SECONDS.
    """
    slack = _slack_connector()

    # Post notification
    text = f"HITL approval required for run `{run_id}` — skill: `{skill}`"
    blocks = _build_approval_blocks(run_id, skill, reason, step)
    resp = slack.post_message(HITL_SLACK_CHANNEL, text=text, blocks=blocks)
    message_ts = resp.get("ts", "")
    channel_id = resp.get("channel", "")

    logger.info("HITL notification posted to %s (ts=%s)", HITL_SLACK_CHANNEL, message_ts)

    # Poll for reactions
    deadline = time.monotonic() + HITL_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        time.sleep(HITL_POLL_INTERVAL)
        try:
            reactions_resp = slack._slack_request(
                "GET",
                f"reactions.get?channel={channel_id}&timestamp={message_ts}&full=true",
            )
            reactions = reactions_resp.get("message", {}).get("reactions", [])
            for reaction in reactions:
                emoji = reaction.get("name", "")
                users = reaction.get("users", [])
                authorized_reactors = (
                    set(users) & HITL_AUTHORIZED_USERS
                    if HITL_AUTHORIZED_USERS
                    else set(users)
                )
                if not authorized_reactors:
                    continue

                approver_id = next(iter(authorized_reactors))

                if emoji == APPROVE_EMOJI:
                    logger.info("HITL approved by %s for run %s", approver_id, run_id)
                    return True, approver_id

                if emoji == REJECT_EMOJI:
                    logger.info("HITL rejected by %s for run %s", approver_id, run_id)
                    return False, approver_id

        except Exception as exc:
            logger.warning("Error polling Slack reactions: %s", exc)

    raise TimeoutError(
        f"HITL approval timed out after {HITL_TIMEOUT_SECONDS}s for run {run_id}"
    )


def handle_hitl_event(
    run_id: str,
    skill: str,
    reason: str,
    step: int = 0,
) -> None:
    """
    Full HITL lifecycle: notify Slack → poll → send Temporal signal.

    This is called by the workflow runtime when a HITL gate is triggered.
    Blocks until approval, rejection, or timeout.
    """
    logger.info("HITL gate triggered for run %s skill %s", run_id, skill)
    try:
        approved, approver = notify_and_wait(run_id, skill, reason, step)
        if approved:
            approve_workflow(run_id, approver=approver, justification="Approved via Slack reaction")
        else:
            reject_workflow(run_id, approver=approver, reason="Rejected via Slack reaction")
    except TimeoutError as exc:
        logger.error("HITL timeout: %s", exc)
        reject_workflow(run_id, approver="system", reason=f"Auto-rejected: timeout ({HITL_TIMEOUT_SECONDS}s)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse

    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"),
                        format="%(asctime)s %(levelname)s %(name)s — %(message)s")

    parser = argparse.ArgumentParser(description="Apotheon HITL handler")
    sub = parser.add_subparsers(dest="cmd")

    notify_p = sub.add_parser("notify", help="Post HITL notification and wait for approval")
    notify_p.add_argument("run_id")
    notify_p.add_argument("--skill", default="unknown")
    notify_p.add_argument("--reason", default="HITL gate triggered")
    notify_p.add_argument("--step", type=int, default=0)

    approve_p = sub.add_parser("approve", help="Approve a paused workflow")
    approve_p.add_argument("run_id")
    approve_p.add_argument("--reason", default="Approved via CLI")

    reject_p = sub.add_parser("reject", help="Reject a paused workflow")
    reject_p.add_argument("run_id")
    reject_p.add_argument("--reason", default="Rejected via CLI")

    args = parser.parse_args()

    if args.cmd == "notify":
        try:
            handle_hitl_event(args.run_id, args.skill, args.reason, args.step)
        except Exception as exc:
            logger.error("HITL handler failed: %s", exc)
            return 1
        return 0

    if args.cmd == "approve":
        try:
            approve_workflow(args.run_id, approver=os.environ.get("USER", "operator"), justification=args.reason)
            print(f"Approved: {args.run_id}")
        except Exception as exc:
            logger.error("Approve failed: %s", exc)
            return 1
        return 0

    if args.cmd == "reject":
        try:
            reject_workflow(args.run_id, approver=os.environ.get("USER", "operator"), reason=args.reason)
            print(f"Rejected: {args.run_id}")
        except Exception as exc:
            logger.error("Reject failed: %s", exc)
            return 1
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())