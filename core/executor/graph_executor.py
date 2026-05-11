from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class NodeState:
    status: str = "pending"
    attempts: int = 0


class GraphExecutor:
    """Executes workflow graph with branch/retry/approval/checkpoint support."""

    def __init__(self, handlers: dict[str, Any]) -> None:
        self.handlers = handlers

    def _ready(self, node: dict[str, Any], states: dict[str, NodeState], edges: list[dict[str, Any]]) -> bool:
        incoming = [e for e in edges if e["to"] == node["id"]]
        for edge in incoming:
            from_state = states[edge["from"]]
            condition = edge.get("when", "success")
            if condition == "success" and from_state.status != "succeeded":
                return False
            if condition == "failure" and from_state.status != "failed":
                return False
        return True

    def run(self, graph: dict[str, Any], state: dict[str, Any] | None = None) -> dict[str, Any]:
        state = state or {}
        nodes = {n["id"]: n for n in graph["nodes"]}
        edges = graph.get("edges", [])
        memory = dict(state.get("memory", {}))
        node_states: dict[str, NodeState] = {
            nid: NodeState(**s) if isinstance(s, dict) else NodeState() for nid, s in state.get("node_states", {}).items()
        }
        for nid in nodes:
            node_states.setdefault(nid, NodeState())

        progressed = True
        while progressed:
            progressed = False
            for nid, node in nodes.items():
                ns = node_states[nid]
                if ns.status in {"succeeded", "failed", "blocked"}:
                    continue
                if not self._ready(node, node_states, edges):
                    continue
                required_memory = node.get("memory", {}).get("requires", [])
                if any(key not in memory for key in required_memory):
                    ns.status = "blocked"
                    continue
                if node.get("approval", {}).get("required") and nid not in state.get("approvals", {}):
                    ns.status = "awaiting_approval"
                    continue
                retry_max = int((node.get("retry") or {}).get("max_attempts", 1))
                handler = self.handlers[node.get("kind", "task")]
                ns.attempts += 1
                result = handler(node, memory)
                progressed = True
                if result.get("ok"):
                    ns.status = "succeeded"
                    memory.update(result.get("memory", {}))
                elif ns.attempts < retry_max:
                    ns.status = "pending"
                else:
                    ns.status = "failed"

        return {
            "memory": memory,
            "node_states": {nid: ns.__dict__ for nid, ns in node_states.items()},
            "completed": all(ns.status in {"succeeded", "failed", "blocked", "awaiting_approval"} for ns in node_states.values()),
        }
