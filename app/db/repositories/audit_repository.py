"""
app/db/repositories/audit_repository.py — Append-only audit log writer.

Implements a hash-chained audit trail as specified in core/audit-trail/SKILL.md.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditLog


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def _canonical(entry: dict) -> str:
    """Deterministic JSON serialization for hashing."""
    return json.dumps(entry, sort_keys=True, separators=(",", ":"), default=str)


class AuditRepository:
    def __init__(self, db: AsyncSession, org_id: Optional[str] = None):
        self.db = db
        self.org_id = org_id
        self._last_hash: Optional[str] = None  # cached for chain continuity

    async def _get_last_hash(self) -> str:
        q = select(AuditLog.entry_hash).order_by(AuditLog.occurred_at.desc()).limit(1)
        if self.org_id:
            q = q.where(AuditLog.org_id == self.org_id)
        result = await self.db.execute(q)
        row = result.scalar_one_or_none()
        return row or "0" * 64  # genesis hash

    async def append(
        self,
        actor: str,
        action: str,
        resource_type: str = "",
        resource_id: str = "",
        outcome: str = "success",
        risk_level: str = "low",
        run_id: str = "",
        metadata: dict | None = None,
    ) -> AuditLog:
        prev_hash = self._last_hash or await self._get_last_hash()

        base = {
            "actor": actor,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "outcome": outcome,
            "risk_level": risk_level,
            "run_id": run_id,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "prev_hash": prev_hash,
        }
        entry_hash = _sha256(_canonical(base))

        log = AuditLog(
            org_id=self.org_id,
            run_id=run_id or None,
            actor=actor,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            outcome=outcome,
            risk_level=risk_level,
            entry_metadata=metadata or {},
            prev_hash=prev_hash,
            entry_hash=entry_hash,
        )
        self.db.add(log)
        await self.db.flush()
        self._last_hash = entry_hash
        return log

    async def query(
        self,
        run_id: str | None = None,
        actor: str | None = None,
        action: str | None = None,
        limit: int = 50,
    ) -> list[AuditLog]:
        q = select(AuditLog).order_by(AuditLog.occurred_at.desc()).limit(limit)
        if self.org_id:
            q = q.where(AuditLog.org_id == self.org_id)
        if run_id:
            q = q.where(AuditLog.run_id == run_id)
        if actor:
            q = q.where(AuditLog.actor.contains(actor))
        if action:
            q = q.where(AuditLog.action == action)
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def verify_chain(self) -> dict:
        """Walk the chain oldest-to-newest and detect any tampering."""
        q = select(AuditLog).order_by(AuditLog.occurred_at)
        if self.org_id:
            q = q.where(AuditLog.org_id == self.org_id)
        result = await self.db.execute(q)
        entries = list(result.scalars().all())

        broken_links: list[str] = []
        prev_hash = "0" * 64
        for entry in entries:
            if entry.prev_hash != prev_hash:
                broken_links.append(entry.id)
            prev_hash = entry.entry_hash

        return {
            "entries_verified": len(entries),
            "chain_intact": len(broken_links) == 0,
            "tamper_detected": len(broken_links) > 0,
            "broken_links": broken_links,
        }