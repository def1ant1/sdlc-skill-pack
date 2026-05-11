from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PlannedNode:
    node_id: str
    kind: str
    retry_max: int


class GraphPlanner:
    """Normalizes graph nodes for execution."""

    def build_plan(self, graph: dict[str, Any]) -> dict[str, Any]:
        nodes = graph.get("nodes", [])
        normalized = []
        for node in nodes:
            retry = node.get("retry") or {}
            normalized.append(
                PlannedNode(
                    node_id=node["id"],
                    kind=node.get("kind", "task"),
                    retry_max=int(retry.get("max_attempts", 1)),
                ).__dict__
            )
        return {"nodes": normalized, "entrypoint": graph.get("entrypoint")}
