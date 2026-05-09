"""
app/api/v1/memory.py — Semantic memory search endpoint.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.dependencies import CurrentUser, require_permission

router = APIRouter(prefix="/v1/memory", tags=["memory"])

_MEMORY_PATH = str(Path(__file__).parent.parent.parent.parent / "scripts" / "memory")
if _MEMORY_PATH not in sys.path:
    sys.path.insert(0, _MEMORY_PATH)


@router.get("/search")
async def search_memory(
    q: str = Query(..., description="Semantic search query"),
    top_k: int = Query(5, ge=1, le=50),
    min_score: float = Query(0.65, ge=0.0, le=1.0),
    obs_type: str | None = Query(None, description="Filter by obs_type (step_output, context_snapshot, etc.)"),
    user: Annotated[CurrentUser, Depends(require_permission("memory:search"))] = None,
):
    """Embed query and retrieve semantically similar observations from Qdrant."""
    try:
        from retrieve_context import retrieve

        payload_filter = {"obs_type": obs_type} if obs_type else None
        result = retrieve(q, top_k=top_k, min_score=min_score, payload_filter=payload_filter)
        return result
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Memory retrieval unavailable: {exc}")


@router.get("/health")
async def memory_health(
    user: Annotated[CurrentUser, Depends(require_permission("memory:search"))] = None,
):
    """Run the memory health check and return results."""
    _SCRIPTS = str(Path(__file__).parent.parent.parent.parent / "scripts" / "memory")
    if _SCRIPTS not in sys.path:
        sys.path.insert(0, _SCRIPTS)
    try:
        from check_memory_health import run_checks
        checks = run_checks()
        all_ok = all(c["status"] in ("ok", "skipped", "fixed") for c in checks)
        return {"healthy": all_ok, "checks": checks}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Memory health check failed: {exc}")