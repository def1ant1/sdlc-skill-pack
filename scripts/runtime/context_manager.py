#!/usr/bin/env python3
"""
context_manager.py — Cross-run context packet persistence and restoration.

Solves the statelessness problem: when a workflow resumes after a HITL pause,
crash, or restart, the context packet is rebuilt from Qdrant rather than
starting empty.

Lifecycle:
  1. load_context(run_id, objective)     → hydrate context_packet from prior observations
  2. save_step(run_id, step, output)     → persist step decision to Qdrant
  3. save_context(run_id, context_packet) → snapshot full context to Qdrant
  4. finalize(run_id, status)            → mark workflow complete in memory store

Usage (in execute_workflow.py):
    from context_manager import ContextManager
    cm = ContextManager(run_id, objective)
    context_packet = cm.load()
    # ... run steps ...
    cm.save_step(step_num, skill_name, output_text)
    cm.finalize("completed")

Environment variables:
    QDRANT_URL           Qdrant server (default: http://localhost:6333)
    EMBEDDING_BACKEND    ollama | openai (default: ollama)
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger("context_manager")

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE.parent))

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
OBSERVATIONS_COLLECTION = "apotheon-observations"
DECISIONS_COLLECTION = "apotheon-decisions"


# ---------------------------------------------------------------------------
# Qdrant helpers (stdlib only)
# ---------------------------------------------------------------------------

def _qdrant_request(method: str, path: str, payload: dict | None = None) -> dict:
    import urllib.error
    import urllib.request

    url = f"{QDRANT_URL}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {}
        raise


def _embed(text: str) -> list[float] | None:
    """Embed text using configured backend. Returns None if unavailable."""
    try:
        sys.path.insert(0, str(_HERE.parent / "memory"))
        from embed_observation import embed_text
        return embed_text(text)
    except Exception as exc:
        logger.debug("Embedding unavailable: %s", exc)
        return None


# ---------------------------------------------------------------------------
# ContextManager
# ---------------------------------------------------------------------------

class ContextManager:
    """
    Manages context packet persistence across workflow runs via Qdrant.

    All observations are keyed by run_id so multiple concurrent workflows
    don't interfere with each other.
    """

    def __init__(self, run_id: str, objective: str):
        self.run_id = run_id
        self.objective = objective

    # ------------------------------------------------------------------
    # Load — hydrate context from prior state
    # ------------------------------------------------------------------

    def load(self) -> dict[str, Any]:
        """
        Load the context packet for this run_id.

        If a snapshot exists (from a prior partial run), restore it.
        Otherwise return a fresh empty packet.
        """
        snapshot = self._load_snapshot()
        if snapshot:
            logger.info("Restored context snapshot for run %s (%d artifacts)",
                        self.run_id, len(snapshot.get("artifacts", [])))
            return snapshot

        return {
            "objective": self.objective,
            "phase": "",
            "decisions": [],
            "constraints": [],
            "artifacts": [],
            "risks": [],
            "next_action": "",
        }

    def _load_snapshot(self) -> dict | None:
        """Search Qdrant for a context snapshot for this run_id."""
        try:
            resp = _qdrant_request(
                "POST",
                f"/collections/{OBSERVATIONS_COLLECTION}/points/scroll",
                {
                    "filter": {
                        "must": [
                            {"key": "run_id", "match": {"value": self.run_id}},
                            {"key": "obs_type", "match": {"value": "context_snapshot"}},
                        ]
                    },
                    "limit": 1,
                    "with_payload": True,
                    "order_by": {"key": "observed_at", "direction": "desc"},
                },
            )
            points = resp.get("result", {}).get("points", [])
            if points:
                payload = points[0].get("payload", {})
                return json.loads(payload.get("context_json", "{}"))
        except Exception as exc:
            logger.debug("Could not load context snapshot: %s", exc)
        return None

    # ------------------------------------------------------------------
    # Save — persist decisions and snapshots
    # ------------------------------------------------------------------

    def save_step(self, step: int, skill: str, output: str) -> None:
        """Persist a completed step's output as an observation."""
        obs_id = f"{self.run_id}-step-{step}"
        text = f"[{skill}] Step {step} output:\n{output[:2000]}"
        vector = _embed(text)

        if vector is None:
            logger.debug("Skipping Qdrant upsert — embedding unavailable")
            return

        import uuid
        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, obs_id))
        payload = {
            "run_id": self.run_id,
            "obs_id": obs_id,
            "obs_type": "step_output",
            "skill": skill,
            "step": step,
            "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "output_preview": output[:500],
        }

        _qdrant_request(
            "PUT",
            f"/collections/{OBSERVATIONS_COLLECTION}/points",
            {"points": [{"id": point_id, "vector": vector, "payload": payload}]},
        )
        logger.debug("Saved step %d observation for run %s", step, self.run_id)

    def save_context(self, context_packet: dict[str, Any]) -> None:
        """Snapshot the full context packet to Qdrant for resumption."""
        obs_id = f"{self.run_id}-context-snapshot-{int(time.time())}"
        text = f"Context snapshot for {self.run_id}: {json.dumps(context_packet)[:1000]}"
        vector = _embed(text)

        if vector is None:
            logger.debug("Skipping context snapshot — embedding unavailable")
            return

        import uuid
        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, obs_id))
        payload = {
            "run_id": self.run_id,
            "obs_id": obs_id,
            "obs_type": "context_snapshot",
            "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "context_json": json.dumps(context_packet),
        }

        _qdrant_request(
            "PUT",
            f"/collections/{OBSERVATIONS_COLLECTION}/points",
            {"points": [{"id": point_id, "vector": vector, "payload": payload}]},
        )
        logger.debug("Saved context snapshot for run %s", self.run_id)

    def save_decision(self, decision: str, skill: str, step: int) -> None:
        """Write a decision record to the apotheon-decisions collection."""
        import uuid
        decision_id = f"{self.run_id}-decision-{step}"
        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, decision_id))
        vector = _embed(decision)
        if vector is None:
            return

        payload = {
            "decision_id": decision_id,
            "run_id": self.run_id,
            "decision_type": "skill_output",
            "skill": skill,
            "step": step,
            "decided_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "outcome": decision[:500],
        }

        _qdrant_request(
            "PUT",
            f"/collections/{DECISIONS_COLLECTION}/points",
            {"points": [{"id": point_id, "vector": vector, "payload": payload}]},
        )

    def finalize(self, status: str) -> None:
        """Mark the workflow as finalized with a terminal status observation."""
        obs_id = f"{self.run_id}-finalized"
        text = f"Workflow {self.run_id} finalized with status: {status}"
        vector = _embed(text)
        if vector is None:
            return

        import uuid
        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, obs_id))
        payload = {
            "run_id": self.run_id,
            "obs_id": obs_id,
            "obs_type": "workflow_finalized",
            "status": status,
            "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        _qdrant_request(
            "PUT",
            f"/collections/{OBSERVATIONS_COLLECTION}/points",
            {"points": [{"id": point_id, "vector": vector, "payload": payload}]},
        )
        logger.info("Finalized run %s as %s", self.run_id, status)

    # ------------------------------------------------------------------
    # Retrieve — semantic search over prior runs
    # ------------------------------------------------------------------

    def retrieve_relevant(self, query: str, top_k: int = 5) -> list[dict]:
        """Return top_k prior observations semantically similar to query."""
        vector = _embed(query)
        if vector is None:
            return []
        try:
            resp = _qdrant_request(
                "POST",
                f"/collections/{OBSERVATIONS_COLLECTION}/points/search",
                {
                    "vector": vector,
                    "limit": top_k,
                    "with_payload": True,
                    "score_threshold": 0.6,
                },
            )
            return resp.get("result", [])
        except Exception as exc:
            logger.debug("Retrieval failed: %s", exc)
            return []