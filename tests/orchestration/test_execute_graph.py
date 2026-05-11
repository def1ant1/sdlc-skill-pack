from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXECUTOR_PATH = ROOT / "core" / "executor" / "graph_executor.py"


spec = importlib.util.spec_from_file_location("graph_executor", EXECUTOR_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)
GraphExecutor = module.GraphExecutor


def handler(node, memory):
    count_key = f"count:{node['id']}"
    memory[count_key] = memory.get(count_key, 0) + 1
    if memory[count_key] <= int(node.get("fail_until", 0)):
        return {"ok": False}
    return {"ok": True, "memory": node.get("produce", {})}


def test_branching_and_retry_semantics():
    graph = {
        "entrypoint": "start",
        "nodes": [
            {"id": "start", "kind": "task", "produce": {"route": "A"}},
            {"id": "branchA", "kind": "task", "memory": {"requires": ["route"]}, "fail_until": 1, "retry": {"max_attempts": 2}},
            {"id": "onFailure", "kind": "task"},
        ],
        "edges": [
            {"from": "start", "to": "branchA", "when": "success"},
            {"from": "branchA", "to": "onFailure", "when": "failure"},
        ],
    }
    result = GraphExecutor({"task": handler}).run(graph)
    assert result["node_states"]["start"]["status"] == "succeeded"
    assert result["node_states"]["branchA"]["status"] == "succeeded"
    assert result["node_states"]["branchA"]["attempts"] == 2
    assert result["node_states"]["onFailure"]["status"] == "pending"


def test_approval_checkpoint_and_resume():
    graph = {
        "entrypoint": "gate",
        "nodes": [
            {"id": "gate", "kind": "task", "approval": {"required": True}, "produce": {"approved": True}},
            {"id": "after", "kind": "task", "memory": {"requires": ["approved"]}},
        ],
        "edges": [{"from": "gate", "to": "after", "when": "success"}],
    }
    executor = GraphExecutor({"task": handler})
    checkpoint = executor.run(graph, state={})
    assert checkpoint["node_states"]["gate"]["status"] == "awaiting_approval"

    resumed = executor.run(graph, state={"approvals": {"gate": True}, **checkpoint})
    assert resumed["node_states"]["gate"]["status"] == "succeeded"
    assert resumed["node_states"]["after"]["status"] == "succeeded"
