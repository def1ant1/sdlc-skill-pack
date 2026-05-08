#!/usr/bin/env python3
"""
init_collections.py — Initialize Qdrant collections for Apotheon memory.

Creates the following collections if they do not already exist:
  - apotheon-observations   (main observation store)
  - apotheon-knowledge      (institutional knowledge index)
  - apotheon-decisions      (decision records)

Embedding dimensions default to 768 (nomic-embed-text) or 1536 (text-embedding-3-small).

Usage:
    python scripts/memory/init_collections.py
    python scripts/memory/init_collections.py --dims 1536 --distance Cosine

Environment variables:
    QDRANT_URL           Qdrant server URL (default: http://localhost:6333)
    EMBEDDING_DIMS       Vector dimensions (default: 768)
"""
from __future__ import annotations

import json
import logging
import os
import sys
import urllib.request
import urllib.error

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("init_collections")

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
DEFAULT_DIMS = int(os.environ.get("EMBEDDING_DIMS", "768"))

COLLECTIONS: list[dict] = [
    {
        "name": "apotheon-observations",
        "description": "Primary observation store: events, decisions, summaries",
        "payload_schema": {
            "obs_id": "keyword",
            "obs_type": "keyword",
            "entities": "keyword[]",
            "observed_at": "keyword",
            "source_type": "keyword",
            "salience": "float",
            "compressed": "bool",
        },
    },
    {
        "name": "apotheon-knowledge",
        "description": "Institutional knowledge index: lessons, decisions, runbooks, standards",
        "payload_schema": {
            "entry_id": "keyword",
            "source_type": "keyword",
            "source_id": "keyword",
            "tags": "keyword[]",
            "data_classification": "keyword",
            "searchable": "bool",
            "archived": "bool",
        },
    },
    {
        "name": "apotheon-decisions",
        "description": "Decision records with full context for archaeology queries",
        "payload_schema": {
            "decision_id": "keyword",
            "decision_type": "keyword",
            "entities": "keyword[]",
            "decided_at": "keyword",
            "outcome": "keyword",
        },
    },
]


def collection_exists(name: str) -> bool:
    try:
        req = urllib.request.Request(
            f"{QDRANT_URL}/collections/{name}",
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=5):
            return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise


def create_collection(name: str, dims: int, distance: str = "Cosine") -> None:
    payload = {
        "vectors": {
            "size": dims,
            "distance": distance,
        },
        "optimizers_config": {
            "default_segment_number": 2,
        },
        "replication_factor": 1,
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{QDRANT_URL}/collections/{name}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="PUT",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())
    if result.get("result") is not True:
        raise RuntimeError(f"Unexpected response creating collection '{name}': {result}")


def create_payload_index(collection: str, field_name: str, field_type: str) -> None:
    """Create a payload index for efficient filtering."""
    # Normalize field type for Qdrant
    qdrant_type = "keyword" if field_type in ("keyword", "keyword[]") else field_type
    payload = {"field_name": field_name, "field_schema": qdrant_type}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{QDRANT_URL}/collections/{collection}/index",
        data=data,
        headers={"Content-Type": "application/json"},
        method="PUT",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        resp.read()  # discard; status check below handled by urllib exception on non-2xx


def init_all(dims: int = DEFAULT_DIMS, distance: str = "Cosine") -> dict:
    results = {}
    for col in COLLECTIONS:
        name = col["name"]
        if collection_exists(name):
            logger.info("Collection '%s' already exists — skipping", name)
            results[name] = "exists"
        else:
            logger.info("Creating collection '%s' (dims=%d, distance=%s)", name, dims, distance)
            create_collection(name, dims=dims, distance=distance)

            # Create payload indexes for filterable fields
            for field, ftype in col["payload_schema"].items():
                try:
                    create_payload_index(name, field, ftype)
                    logger.debug("Indexed payload field '%s' (%s)", field, ftype)
                except Exception as exc:
                    logger.warning("Could not index field '%s': %s", field, exc)

            logger.info("Collection '%s' created successfully", name)
            results[name] = "created"

    return results


def main() -> int:
    args = sys.argv[1:]
    dims = DEFAULT_DIMS
    distance = "Cosine"

    i = 0
    while i < len(args):
        if args[i] == "--dims" and i + 1 < len(args):
            dims = int(args[i + 1])
            i += 2
        elif args[i] == "--distance" and i + 1 < len(args):
            distance = args[i + 1]
            i += 2
        else:
            i += 1

    try:
        results = init_all(dims=dims, distance=distance)
        print(json.dumps({"status": "ok", "collections": results}, indent=2))
        return 0
    except Exception as exc:
        logger.error("init_collections failed: %s", exc, exc_info=True)
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())