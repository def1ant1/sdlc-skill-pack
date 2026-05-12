from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from typing import Any

from .models import ArtifactBase


class ArtifactStore:
    """In-memory artifact storage with versioned edits and undo support."""

    def __init__(self) -> None:
        self._artifacts: dict[str, ArtifactBase] = {}
        self._history: dict[str, list[dict[str, Any]]] = {}

    def list_artifacts(self) -> list[ArtifactBase]:
        return list(self._artifacts.values())

    def upsert(self, artifact: ArtifactBase, actor: str = "system") -> None:
        previous = self._artifacts.get(artifact.id)
        if previous:
            self._record_snapshot(previous)
            artifact.version = self._bump_patch(previous.version)
            artifact.create_audit_event("artifact.updated", actor, {"previous_version": previous.version})
        else:
            artifact.create_audit_event("artifact.created", actor)
        self._artifacts[artifact.id] = artifact

    def link(self, artifact_id: str, rel: str, target: str, actor: str = "system") -> None:
        artifact = self._artifacts[artifact_id]
        artifact.links.append({"rel": rel, "target": target})
        artifact.create_audit_event("artifact.linked", actor, {"rel": rel, "target": target})

    def undo(self, artifact_id: str, actor: str = "system") -> bool:
        history = self._history.get(artifact_id, [])
        if not history:
            return False
        restored = history.pop()
        current = self._artifacts[artifact_id]
        current.create_audit_event("artifact.reverted", actor, {"to_version": restored.get("version")})
        self._artifacts[artifact_id] = ArtifactBase(**restored)
        return True

    def _record_snapshot(self, artifact: ArtifactBase) -> None:
        self._history.setdefault(artifact.id, []).append(deepcopy(asdict(artifact)))

    @staticmethod
    def _bump_patch(version: str) -> str:
        major, minor, patch = [int(part) for part in version.split(".")]
        return f"{major}.{minor}.{patch + 1}"
