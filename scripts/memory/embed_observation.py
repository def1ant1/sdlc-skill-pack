#!/usr/bin/env python3
"""
embed_observation.py — Embed an observation and upsert it to the vector store.

Reads an observation JSON from stdin (or --input flag) and persists it to Qdrant
with a text embedding. Requires QDRANT_URL and an embedding backend configured
via EMBEDDING_BACKEND env var (ollama | openai).

Usage:
    echo '{"obs_id": "OBS-001", "content": "Sprint 22 completed. Velocity: 42.", "entities": ["sprint-22"], "obs_type": "event"}' \
        | python scripts/memory/embed_observation.py

    python scripts/memory/embed_observation.py --input observation.json

Environment variables:
    QDRANT_URL            Qdrant server URL (default: http://localhost:6333)
    QDRANT_COLLECTION     Collection name (default: apotheon-observations)
    EMBEDDING_BACKEND     ollama | openai (default: ollama)
    OLLAMA_URL            Ollama server URL (default: http://localhost:11434)
    OLLAMA_MODEL          Embedding model (default: nomic-embed-text)
    OPENAI_API_KEY        Required if EMBEDDING_BACKEND=openai
    OPENAI_EMBED_MODEL    OpenAI embedding model (default: text-embedding-3-small)
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
import uuid
from pathlib import Path

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("embed_observation")

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.environ.get("QDRANT_COLLECTION", "apotheon-observations")
EMBEDDING_BACKEND = os.environ.get("EMBEDDING_BACKEND", "ollama")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "nomic-embed-text")
OPENAI_EMBED_MODEL = os.environ.get("OPENAI_EMBED_MODEL", "text-embedding-3-small")


def embed_text(text: str) -> list[float]:
    """Generate a text embedding using the configured backend."""
    if EMBEDDING_BACKEND == "openai":
        return _embed_openai(text)
    return _embed_ollama(text)


def _embed_ollama(text: str) -> list[float]:
    """Embed text via Ollama's /api/embeddings endpoint."""
    import urllib.request
    payload = json.dumps({"model": OLLAMA_MODEL, "prompt": text}).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/embeddings",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data["embedding"]


def _embed_openai(text: str) -> list[float]:
    """Embed text via OpenAI embeddings API."""
    import urllib.request
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is required when EMBEDDING_BACKEND=openai")
    payload = json.dumps({"input": text, "model": OPENAI_EMBED_MODEL}).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/embeddings",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data["data"][0]["embedding"]


def upsert_to_qdrant(obs: dict, vector: list[float]) -> None:
    """Upsert a point to Qdrant."""
    import urllib.request
    point_id = obs.get("obs_id", str(uuid.uuid4()))
    payload = {
        "points": [
            {
                "id": _stable_uuid(point_id),
                "vector": vector,
                "payload": {
                    "obs_id": obs.get("obs_id", ""),
                    "content": obs.get("content", ""),
                    "entities": obs.get("entities", []),
                    "obs_type": obs.get("obs_type", "event"),
                    "observed_at": obs.get("observed_at", ""),
                    "source_type": obs.get("source_type", ""),
                    "salience": obs.get("salience", 0.5),
                    "compressed": obs.get("compressed", False),
                },
            }
        ]
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{QDRANT_URL}/collections/{COLLECTION}/points",
        data=data,
        headers={"Content-Type": "application/json"},
        method="PUT",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())
    if result.get("status") != "ok":
        raise RuntimeError(f"Qdrant upsert failed: {result}")


def _stable_uuid(obs_id: str) -> str:
    """Deterministic UUID from obs_id string for idempotent upserts."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"apotheon:obs:{obs_id}"))


def embed_and_store(obs: dict) -> dict:
    """Main pipeline: embed text → upsert to Qdrant. Returns result summary."""
    content = obs.get("content", "")
    if not content:
        raise ValueError("Observation must have non-empty 'content' field")

    logger.info("Embedding observation %s (%d chars)", obs.get("obs_id", "?"), len(content))
    t0 = time.perf_counter()
    vector = embed_text(content)
    embed_ms = int((time.perf_counter() - t0) * 1000)
    logger.info("Embedding complete in %dms (dims=%d)", embed_ms, len(vector))

    upsert_to_qdrant(obs, vector)
    logger.info("Upserted to Qdrant collection '%s'", COLLECTION)

    return {
        "obs_id": obs.get("obs_id", ""),
        "collection": COLLECTION,
        "embedding_dims": len(vector),
        "embed_latency_ms": embed_ms,
        "status": "ok",
    }


def main() -> int:
    args = sys.argv[1:]
    input_path: str | None = None
    i = 0
    while i < len(args):
        if args[i] == "--input" and i + 1 < len(args):
            input_path = args[i + 1]
            i += 2
        else:
            i += 1

    try:
        if input_path:
            obs = json.loads(Path(input_path).read_text(encoding="utf-8"))
        else:
            obs = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to read observation input: %s", exc)
        return 1

    try:
        result = embed_and_store(obs)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        logger.error("embed_and_store failed: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())