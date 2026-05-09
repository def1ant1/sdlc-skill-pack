"""
app/api/v1/connectors.py — Connector registry, health, and lifecycle endpoints.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import CurrentUser, require_permission

router = APIRouter(prefix="/v1/connectors", tags=["connectors"])

_CONNECTORS_PATH = str(Path(__file__).parent.parent.parent.parent / "scripts" / "connectors")
if _CONNECTORS_PATH not in sys.path:
    sys.path.insert(0, _CONNECTORS_PATH)


@router.get("")
async def list_connectors(
    user: Annotated[CurrentUser, Depends(require_permission("connector:read"))] = None,
):
    """List all registered connectors with last known health status."""
    try:
        from health_check import CONNECTOR_REGISTRY
        return [
            {"connector": name, "module": mod, "class": cls}
            for name, (mod, cls) in CONNECTOR_REGISTRY.items()
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/{connector_id}/health-check")
async def connector_health_check(
    connector_id: str,
    user: Annotated[CurrentUser, Depends(require_permission("connector:health"))] = None,
):
    """Trigger a live health check for a specific connector."""
    try:
        from health_check import CONNECTOR_REGISTRY, check_connector
        if connector_id not in CONNECTOR_REGISTRY:
            raise HTTPException(status_code=404, detail=f"Connector {connector_id!r} not registered")
        mod, cls = CONNECTOR_REGISTRY[connector_id]
        result = check_connector(connector_id, mod, cls)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/health")
async def all_connector_health(
    user: Annotated[CurrentUser, Depends(require_permission("connector:health"))] = None,
):
    """Run health checks for all registered connectors."""
    try:
        from health_check import run_checks
        return run_checks()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))