#!/usr/bin/env python3
"""
retrieve_context.py — Semantic retrieval from the Qdrant observation store.

Embeds a query string and retrieves the top-k most relevant observations,
with optional metadata filtering.

Usage:
    python scripts/memory/retrieve_context.py "how did we resolve the DB connection pool issue?"

    python scripts/memory/retrieve_context.py \\
        --query "sprint 22 velocity" \\
        --top-k 10 \\
        --min-score 0.70 \\
        --filter '{"obs_type": "event"}'

Environment variables:
    QDRANT_URL            Qdrant server URL (default: http://localhost:6333)
    QDRANT_COLLECTION     Collection name (default: apotheon-observations)
    EMBEDDING_BACKEND     ollama | openai (default: ollama)
    (see embed_observation.py for full env var list)
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("retrieve_context")

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.environ.get("QDRANT_COLLECTION", "apotheon-observations")

# Import embed_text from embed_observation (sibling script)
_HERE = __file__
sys.path.insert(0, str(__import__("pathlib").Path(_HERE).parent))
from embed_observation import embed_text  # noqa: E402
from detect_contradictions import detect  # noqa: E402


def search_qdrant(
    vector: list[float],
    top_k: int = 5,
    min_score: float = 0.70,
    payload_filter: dict | None = None,
) -> list[dict]:
    """Perform a vector similarity search in Qdrant."""
    import urllib.request

    query: dict = {
        "vector": vector,
        "limit": top_k,
        "score_threshold": min_score,
        "with_payload": True,
    }
    if payload_filter:
        # Build a simple must-match filter for exact payload values
        must_conditions = [
            {"key": k, "match": {"value": v}}
            for k, v in payload_filter.items()
        ]
        query["filter"] = {"must": must_conditions}

    data = json.dumps(query).encode()
    req = urllib.request.Request(
        f"{QDRANT_URL}/collections/{COLLECTION}/points/search",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())

    return result.get("result", [])


def retrieve(
    query: str,
    top_k: int = 5,
    min_score: float = 0.70,
    payload_filter: dict | None = None,
) -> dict:
    """Embed a query and retrieve relevant observations."""
    logger.info("Embedding query (%d chars)", len(query))
    t0 = time.perf_counter()
    vector = embed_text(query)
    embed_ms = int((time.perf_counter() - t0) * 1000)
    logger.info("Embedding complete in %dms", embed_ms)

    hits = search_qdrant(vector, top_k=top_k, min_score=min_score, payload_filter=payload_filter)
    logger.info("Retrieved %d results (min_score=%.2f)", len(hits), min_score)

    # Format output
    results = []
    for hit in hits:
        payload = hit.get("payload", {})
        results.append({
            "score": round(hit.get("score", 0.0), 4),
            "obs_id": payload.get("obs_id", ""),
            "content": payload.get("content", ""),
            "obs_type": payload.get("obs_type", ""),
            "entities": payload.get("entities", []),
            "observed_at": payload.get("observed_at", ""),
            "salience": payload.get("salience", 0.0),
        })

    contradiction_report = detect([{
        "event_id": r["obs_id"],
        "content": r["content"],
        "entity_refs": [{"entity_type": e.split(":", 1)[0], "entity_id": e.split(":", 1)[1]} for e in r.get("entities", []) if isinstance(e, str) and ":" in e],
    } for r in results])

    if contradiction_report.get("blocked"):
        return {
            "query": query,
            "blocked": True,
            "contradictions": contradiction_report.get("contradictions", []),
            "result_count": 0,
            "results": [],
        }

    return {
        "query": query,
        "top_k": top_k,
        "min_score": min_score,
        "result_count": len(results),
        "embed_latency_ms": embed_ms,
        "results": results,
    }


def main() -> int:
    args = sys.argv[1:]
    query: str = ""
    top_k: int = 5
    min_score: float = 0.70
    payload_filter: dict | None = None

    i = 0
    while i < len(args):
        if args[i] == "--query" and i + 1 < len(args):
            query = args[i + 1]
            i += 2
        elif args[i] == "--top-k" and i + 1 < len(args):
            top_k = int(args[i + 1])
            i += 2
        elif args[i] == "--min-score" and i + 1 < len(args):
            min_score = float(args[i + 1])
            i += 2
        elif args[i] == "--filter" and i + 1 < len(args):
            payload_filter = json.loads(args[i + 1])
            i += 2
        elif not args[i].startswith("--"):
            query = args[i]
            i += 1
        else:
            i += 1

    if not query:
        print("Usage: retrieve_context.py <query> [--top-k N] [--min-score F] [--filter JSON]",
              file=sys.stderr)
        return 1

    try:
        result = retrieve(query, top_k=top_k, min_score=min_score, payload_filter=payload_filter)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        logger.error("Retrieval failed: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())