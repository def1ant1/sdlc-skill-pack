"""
app/auth/rbac.py — Role-based access control.

Role hierarchy: VIEWER < DEVELOPER < OPERATOR < ADMIN
"""
from __future__ import annotations

from enum import IntEnum


class Role(IntEnum):
    VIEWER = 1
    DEVELOPER = 2
    OPERATOR = 3
    ADMIN = 4

    @classmethod
    def from_str(cls, s: str) -> "Role":
        mapping = {
            "viewer": cls.VIEWER,
            "developer": cls.DEVELOPER,
            "operator": cls.OPERATOR,
            "admin": cls.ADMIN,
        }
        return mapping.get(s.lower(), cls.VIEWER)


# Permission matrix: action -> minimum role required
PERMISSIONS: dict[str, Role] = {
    # Workflows
    "workflow:submit": Role.DEVELOPER,
    "workflow:read": Role.VIEWER,
    "workflow:cancel": Role.OPERATOR,
    "workflow:delete": Role.ADMIN,
    # Approvals
    "approval:read": Role.VIEWER,
    "approval:decide": Role.OPERATOR,
    # Memory
    "memory:search": Role.DEVELOPER,
    "memory:write": Role.DEVELOPER,
    # Connectors
    "connector:read": Role.VIEWER,
    "connector:health": Role.DEVELOPER,
    "connector:register": Role.ADMIN,
    "connector:activate": Role.OPERATOR,
    # Governance
    "policy:read": Role.VIEWER,
    "policy:write": Role.ADMIN,
    "governance:dashboard": Role.OPERATOR,
    # Telemetry
    "telemetry:read": Role.VIEWER,
    # Users / Org
    "user:read": Role.OPERATOR,
    "user:write": Role.ADMIN,
    "org:read": Role.OPERATOR,
    "org:write": Role.ADMIN,
    # Cost
    "cost:estimate": Role.DEVELOPER,
}


def check_permission(role: str | Role, action: str) -> bool:
    """Return True if the role has permission to perform the action."""
    if isinstance(role, str):
        role = Role.from_str(role)
    required = PERMISSIONS.get(action)
    if required is None:
        return False  # unknown action — deny by default
    return role >= required