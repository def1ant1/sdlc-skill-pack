#!/usr/bin/env python3
"""Record execution memory events and promote stable facts to semantic memory."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(".apotheon/memory")
EPISODIC = BASE / "episodic.jsonl"
SEMANTIC = BASE / "semantic.jsonl"
PROCEDURAL = BASE / "procedural.jsonl"
GRAPH = BASE / "knowledge_graph.json"


ENTITY_BUCKETS = ["customers", "invoices", "products", "vendors", "decisions", "risks", "workflows"]


def _ensure() -> None:
    BASE.mkdir(parents=True, exist_ok=True)
    if not GRAPH.exists():
        GRAPH.write_text(json.dumps({"nodes": [], "edges": []}, indent=2), encoding="utf-8")


def _append_jsonl(path: Path, event: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, separators=(",", ":")) + "\n")


def _load_graph() -> dict:
    return json.loads(GRAPH.read_text(encoding="utf-8"))


def _store_graph(graph: dict) -> None:
    GRAPH.write_text(json.dumps(graph, indent=2), encoding="utf-8")


def _update_graph(event: dict) -> None:
    graph = _load_graph()
    nodes = graph["nodes"]
    edges = graph["edges"]
    seen = {(n["entity_type"], n["entity_id"]) for n in nodes}

    for ref in event.get("entity_refs", []):
        key = (ref["entity_type"], ref["entity_id"])
        if key not in seen:
            nodes.append({"entity_type": ref["entity_type"], "entity_id": ref["entity_id"]})
            seen.add(key)
        edges.append({
            "from": event["event_id"],
            "to": ref["entity_id"],
            "type": f"mentions_{ref['entity_type']}"
        })

    _store_graph(graph)


def record(event: dict) -> dict:
    _ensure()
    event.setdefault("observed_at", datetime.now(timezone.utc).isoformat())
    event.setdefault("memory_layer", "episodic")

    _append_jsonl(EPISODIC, event)
    _update_graph(event)

    promoted = False
    if event.get("stable_fact") and float(event.get("confidence", 0)) >= 0.8:
        semantic_event = {**event, "memory_layer": "semantic", "promoted_from": "episodic"}
        _append_jsonl(SEMANTIC, semantic_event)
        promoted = True

    if event.get("skill_improvement"):
        procedural_event = {**event, "memory_layer": "procedural"}
        _append_jsonl(PROCEDURAL, procedural_event)

    return {"status": "ok", "event_id": event["event_id"], "promoted_to_semantic": promoted}


if __name__ == "__main__":
    payload = json.load(sys.stdin)
    print(json.dumps(record(payload), indent=2))
