from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ArtifactSourceRef:
    conversation_id: str
    message_ids: list[str] = field(default_factory=list)


@dataclass
class ArtifactLink:
    rel: str
    target: str
    description: str | None = None


@dataclass
class ArtifactBase:
    id: str
    type: str
    title: str
    status: str
    owner: str
    source: ArtifactSourceRef
    version: str = "1.0.0"
    links: list[ArtifactLink] = field(default_factory=list)
    content: dict[str, Any] = field(default_factory=dict)
    audit_events: list[dict[str, Any]] = field(default_factory=list)

    def create_audit_event(self, event: str, actor: str, details: dict[str, Any] | None = None) -> None:
        self.audit_events.append(
            {
                "event": event,
                "actor": actor,
                "version": self.version,
                "timestamp": utc_now(),
                "details": details or {},
            }
        )
