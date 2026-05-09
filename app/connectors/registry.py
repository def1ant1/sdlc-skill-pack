"""
app/connectors/registry.py — Connector lifecycle registry.

State machine: registered -> validated -> active -> retired
                                       -> error (from any state)

Connectors are registered at startup and persist their state to the DB.
"""
from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger("apotheon.connector_registry")

VALID_STATES = ("registered", "validated", "active", "error", "retired")
VALID_TRANSITIONS: dict[str, list[str]] = {
    "registered": ["validated", "error"],
    "validated":  ["active", "error"],
    "active":     ["retired", "error"],
    "error":      ["registered", "retired"],
    "retired":    [],
}


class ConnectorRegistry:
    """
    In-process connector registry with optional DB persistence.

    Usage:
        registry = ConnectorRegistry(db)
        await registry.register("github", "GithubConnector", "1.2.0")
        await registry.transition("github", "validated")
    """

    def __init__(self, db=None):
        self._db = db
        self._connectors: dict[str, dict] = {}

    async def register(
        self,
        name: str,
        connector_class: str,
        version: str,
        config: dict | None = None,
    ) -> dict:
        """Register a connector (idempotent — updates if already registered)."""
        entry = {
            "connector_name": name,
            "connector_class": connector_class,
            "version": version,
            "status": "registered",
            "config": config or {},
        }
        self._connectors[name] = entry

        if self._db:
            await self._persist(name, entry)

        logger.info("Connector registered: %s v%s (%s)", name, version, connector_class)
        return entry

    async def transition(self, name: str, new_state: str, error_detail: str = "") -> dict:
        """Advance connector state machine."""
        if name not in self._connectors:
            raise KeyError(f"Unknown connector: {name}")

        current = self._connectors[name]["status"]
        allowed = VALID_TRANSITIONS.get(current, [])
        if new_state not in allowed:
            raise ValueError(f"Invalid transition {current} -> {new_state} for {name}")

        self._connectors[name]["status"] = new_state
        if error_detail:
            self._connectors[name]["error_detail"] = error_detail

        if self._db:
            await self._persist(name, self._connectors[name])

        logger.info("Connector %s: %s -> %s", name, current, new_state)
        return self._connectors[name]

    def get(self, name: str) -> Optional[dict]:
        return self._connectors.get(name)

    def list_all(self) -> list[dict]:
        return list(self._connectors.values())

    def list_active(self) -> list[dict]:
        return [c for c in self._connectors.values() if c["status"] == "active"]

    async def health_check(self, name: str) -> dict:
        """Run health check for a connector, updating state on failure."""
        connector = self._connectors.get(name)
        if not connector:
            return {"name": name, "status": "unknown", "healthy": False}

        # Attempt to import and ping the connector class
        try:
            module_path, class_name = connector["connector_class"].rsplit(".", 1)
            import importlib
            mod = importlib.import_module(module_path)
            cls = getattr(mod, class_name)
            instance = cls(connector.get("config", {}))
            result = await instance.health()
            if not result.get("healthy", False) and connector["status"] == "active":
                await self.transition(name, "error", error_detail=result.get("detail", "health check failed"))
            return {"name": name, **result}
        except Exception as exc:
            logger.warning("Health check failed for %s: %s", name, exc)
            if connector["status"] == "active":
                await self.transition(name, "error", error_detail=str(exc))
            return {"name": name, "status": "error", "healthy": False, "detail": str(exc)}

    async def _persist(self, name: str, entry: dict) -> None:
        try:
            from sqlalchemy import select
            from app.db.models import ConnectorRegistration

            result = await self._db.execute(
                select(ConnectorRegistration).where(ConnectorRegistration.connector_name == name)
            )
            row = result.scalar_one_or_none()
            if row:
                row.status = entry["status"]
                row.version = entry["version"]
            else:
                self._db.add(ConnectorRegistration(
                    connector_name=name,
                    connector_class=entry["connector_class"],
                    version=entry["version"],
                    status=entry["status"],
                ))
            await self._db.flush()
        except Exception as exc:
            logger.warning("Connector DB persist failed for %s: %s", name, exc)


# Module-level singleton
_registry: Optional[ConnectorRegistry] = None


def get_registry() -> ConnectorRegistry:
    global _registry
    if _registry is None:
        _registry = ConnectorRegistry()
    return _registry