from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ConversationRef:
    session_id: str
    title: str | None = None


@dataclass
class ArtifactRef:
    artifact_id: str
    artifact_type: str
    uri: str | None = None


@dataclass
class ApprovalRef:
    approval_id: str
    run_id: str
    skill_name: str | None = None
    status: str | None = None


@dataclass
class ExecutionRunRef:
    run_id: str
    status: str | None = None


@dataclass
class Workspace:
    workspace_id: str
    name: str
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    active_conversation_id: str | None = None
    conversation_ids: list[str] = field(default_factory=list)
    artifact_ids: list[str] = field(default_factory=list)
    approval_ids: list[str] = field(default_factory=list)
    execution_run_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WorkspaceState:
    schema_version: str
    workspace: Workspace
    conversations: list[ConversationRef] = field(default_factory=list)
    artifacts: list[ArtifactRef] = field(default_factory=list)
    approvals: list[ApprovalRef] = field(default_factory=list)
    execution_runs: list[ExecutionRunRef] = field(default_factory=list)

    def touch(self) -> None:
        self.workspace.updated_at = utc_now()

    def to_dict(self) -> dict:
        return asdict(self)
