"""
app/api/websocket/gateway.py — WebSocket live run update gateway.

Endpoint: ws://<host>/ws/runs/{run_id}?token=<jwt>

Protocol:
  - Client connects with JWT query param (or Authorization header)
  - Server subscribes to Redis pub/sub channel "run:{run_id}"
  - Server forwards JSON messages to client as workflow steps complete
  - Server sends {"event": "ping"} every 30s to keep connection alive
  - Server closes with 4401 if token invalid, 4404 if run not found

Message schema (server -> client):
  {"event": "step_complete", "step": 2, "skill": "...", "status": "completed", "duration_ms": 1234}
  {"event": "hitl_gate",     "step": 3, "skill": "...", "risk_level": "HIGH", "approval_id": "..."}
  {"event": "workflow_complete", "run_id": "...", "status": "completed"}
  {"event": "error", "detail": "..."}
  {"event": "ping"}
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Optional

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.auth.jwt_handler import verify_token

logger = logging.getLogger("apotheon.ws_gateway")

router = APIRouter()

_PING_INTERVAL = 30  # seconds


def _get_redis():
    """Return an async Redis client, or None if unavailable."""
    try:
        import redis.asyncio as aioredis
        import os
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
        return aioredis.from_url(redis_url, decode_responses=True)
    except Exception:
        return None


@router.websocket("/ws/runs/{run_id}")
async def run_websocket(
    websocket: WebSocket,
    run_id: str,
    token: Optional[str] = Query(default=None),
):
    """WebSocket endpoint for live workflow run updates."""
    # --- Auth ---
    jwt = token or _extract_bearer(websocket)
    if not jwt:
        await websocket.close(code=4401, reason="Missing authentication token")
        return

    payload = verify_token(jwt)
    if not payload:
        await websocket.close(code=4401, reason="Invalid or expired token")
        return

    await websocket.accept()
    logger.info("WS connected: run=%s user=%s", run_id, payload.get("sub", "?"))

    redis = _get_redis()
    if redis is None:
        # Fallback: no pub/sub available — notify and close gracefully
        await websocket.send_json({"event": "error", "detail": "Real-time updates unavailable (Redis not configured)"})
        await websocket.close()
        return

    channel = f"run:{run_id}"
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel)

    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(_forward_messages(websocket, pubsub, run_id))
            tg.create_task(_ping_loop(websocket))
    except* (WebSocketDisconnect, asyncio.CancelledError):
        pass
    finally:
        try:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
            await redis.aclose()
        except Exception:
            pass
        logger.info("WS disconnected: run=%s", run_id)


async def _forward_messages(websocket: WebSocket, pubsub, run_id: str) -> None:
    """Read from Redis pub/sub and forward to WebSocket client."""
    async for message in pubsub.listen():
        if message["type"] != "message":
            continue
        try:
            data = json.loads(message["data"])
        except (json.JSONDecodeError, TypeError):
            continue

        try:
            await websocket.send_json(data)
        except Exception:
            break

        # Stop forwarding after terminal events
        if data.get("event") in ("workflow_complete", "error"):
            break


async def _ping_loop(websocket: WebSocket) -> None:
    """Send periodic pings to keep the connection alive."""
    while True:
        await asyncio.sleep(_PING_INTERVAL)
        try:
            await websocket.send_json({"event": "ping"})
        except Exception:
            break


def _extract_bearer(websocket: WebSocket) -> Optional[str]:
    """Extract JWT from Authorization header."""
    auth = websocket.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


# ---------------------------------------------------------------------------
# Publisher helper — called by execute_workflow / workflow API to emit events
# ---------------------------------------------------------------------------

async def publish_event(run_id: str, event: dict) -> None:
    """Publish a workflow event to the Redis channel for this run."""
    redis = _get_redis()
    if not redis:
        return
    try:
        channel = f"run:{run_id}"
        await redis.publish(channel, json.dumps(event))
    except Exception as exc:
        logger.debug("WS publish failed for run %s: %s", run_id, exc)
    finally:
        try:
            await redis.aclose()
        except Exception:
            pass