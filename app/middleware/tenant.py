"""
app/middleware/tenant.py — ContextVar-based tenant isolation middleware.

Stores the authenticated org_id in a ContextVar so it is available
throughout the request lifecycle without threading concerns.

Usage:
    # In any module during a request:
    from app.middleware.tenant import current_org_id
    org = current_org_id.get()
"""
from __future__ import annotations

from contextvars import ContextVar
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# ContextVar — default to empty string (unauthenticated / system context)
current_org_id: ContextVar[str] = ContextVar("current_org_id", default="")
current_user_id: ContextVar[str] = ContextVar("current_user_id", default="")
current_role: ContextVar[str] = ContextVar("current_role", default="viewer")


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Reads org_id / user_id from request state (set by auth dependency)
    and populates ContextVars for downstream use.

    Must be added AFTER authentication middleware so request.state.user exists.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Auth dependencies populate request.state.user (CurrentUser dataclass)
        user = getattr(request.state, "user", None)

        org_token = current_org_id.set(getattr(user, "org_id", "") if user else "")
        uid_token = current_user_id.set(getattr(user, "user_id", "") if user else "")
        role_token = current_role.set(getattr(user, "role", "viewer") if user else "viewer")

        try:
            response = await call_next(request)
        finally:
            current_org_id.reset(org_token)
            current_user_id.reset(uid_token)
            current_role.reset(role_token)

        return response


def get_current_org() -> str:
    """Convenience accessor for the current org_id ContextVar."""
    return current_org_id.get()