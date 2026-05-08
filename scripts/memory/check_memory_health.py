#!/usr/bin/env python3
"""
check_memory_health.py — Preflight checks for the Apotheon memory layer.

Verifies that Qdrant is reachable, required collections exist, and the
configured embedding backend (Ollama or OpenAI) can produce a test embedding.

Usage:
    python scripts/memory/check_memory_health.py
    python scripts/memory/check_memory_health.py --json
    python scripts/memory/check_memory_health.py --fix   # auto-create missing collections

Exit codes:
    0 — all checks passed
    1 — one or more checks failed
"""
from __future__ import annotations

import json
import logging
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "WARNING"),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("check_memory_health")

_HERE = Path(__file__).parent

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "nomic-embed-text")
EMBEDDING_BACKEND = os.environ.get("EMBEDDING_BACKEND", "ollama")

REQUIRED_COLLECTIONS = [
    "apotheon-observations",
    "apotheon-knowledge",
    "apotheon-decisions",
]


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def check_qdrant_reachable() -> dict:
    result = {"check": "qdrant_reachable", "status": "ok", "detail": ""}
    try:
        req = urllib.request.Request(f"{QDRANT_URL}/readyz", method="GET")
        with urllib.request.urlopen(req, timeout=5):
            pass
    except Exception as exc:
        result["status"] = "fail"
        result["detail"] = str(exc)
        result["fix"] = "Start Qdrant: docker compose up -d qdrant"
    return result


def check_qdrant_collections() -> dict:
    result = {"check": "qdrant_collections", "status": "ok", "missing": [], "detail": ""}
    try:
        req = urllib.request.Request(f"{QDRANT_URL}/collections", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        existing = {c["name"] for c in data.get("result", {}).get("collections", [])}
        missing = [c for c in REQUIRED_COLLECTIONS if c not in existing]
        if missing:
            result["status"] = "fail"
            result["missing"] = missing
            result["detail"] = f"Missing collections: {missing}"
            result["fix"] = "Run: python scripts/memory/init_collections.py"
    except Exception as exc:
        result["status"] = "fail"
        result["detail"] = str(exc)
    return result


def check_ollama_reachable() -> dict:
    result = {"check": "ollama_reachable", "status": "ok", "detail": ""}
    if EMBEDDING_BACKEND != "ollama":
        result["status"] = "skipped"
        result["detail"] = f"EMBEDDING_BACKEND={EMBEDDING_BACKEND}"
        return result
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        models = [m.get("name", "") for m in data.get("models", [])]
        # Check the embedding model is pulled
        model_pulled = any(OLLAMA_MODEL in m for m in models)
        if not model_pulled:
            result["status"] = "warn"
            result["detail"] = f"Model '{OLLAMA_MODEL}' not found. Available: {models[:5]}"
            result["fix"] = f"Run: docker exec apotheon-ollama ollama pull {OLLAMA_MODEL}"
    except Exception as exc:
        result["status"] = "fail"
        result["detail"] = str(exc)
        result["fix"] = "Start Ollama: docker compose up -d ollama"
    return result


def check_embedding_works() -> dict:
    result = {"check": "embedding_test", "status": "ok", "detail": ""}
    try:
        sys.path.insert(0, str(_HERE))
        from embed_observation import embed_text
        vector = embed_text("Apotheon memory health check test embedding")
        if not vector or len(vector) < 10:
            result["status"] = "fail"
            result["detail"] = f"Embedding returned unexpected vector: {vector}"
        else:
            result["detail"] = f"Vector dims: {len(vector)}"
    except Exception as exc:
        result["status"] = "fail"
        result["detail"] = str(exc)
        if EMBEDDING_BACKEND == "openai":
            result["fix"] = "Set OPENAI_API_KEY environment variable"
        else:
            result["fix"] = f"Ensure Ollama is running and {OLLAMA_MODEL} is pulled"
    return result


def check_openai_key() -> dict:
    result = {"check": "openai_api_key", "status": "ok", "detail": ""}
    if EMBEDDING_BACKEND != "openai":
        result["status"] = "skipped"
        result["detail"] = f"EMBEDDING_BACKEND={EMBEDDING_BACKEND}"
        return result
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        result["status"] = "fail"
        result["detail"] = "OPENAI_API_KEY not set"
        result["fix"] = "Export OPENAI_API_KEY=sk-..."
    else:
        result["detail"] = f"Key present (prefix: {key[:8]}...)"
    return result


# ---------------------------------------------------------------------------
# Auto-fix
# ---------------------------------------------------------------------------

def _fix_missing_collections(missing: list[str]) -> None:
    sys.path.insert(0, str(_HERE))
    from init_collections import create_collection
    for name in missing:
        dims = int(os.environ.get("EMBEDDING_DIMS", "768"))
        create_collection(name, dims=dims)
        logger.info("Created collection: %s", name)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_checks(fix: bool = False) -> list[dict]:
    checks = [
        check_qdrant_reachable(),
        check_qdrant_collections(),
        check_ollama_reachable(),
        check_openai_key(),
        check_embedding_works(),
    ]

    if fix:
        for check in checks:
            if check["check"] == "qdrant_collections" and check.get("missing"):
                _fix_missing_collections(check["missing"])
                check["status"] = "fixed"

    return checks


def print_table(checks: list[dict]) -> None:
    icons = {"ok": "✓", "fail": "✗", "warn": "!", "skipped": "~", "fixed": "✓"}
    print(f"  {'Check':<30} {'Status':<10} Detail")
    print("  " + "-" * 70)
    for c in checks:
        icon = icons.get(c["status"], "?")
        detail = c.get("detail", "")[:50]
        print(f"  [{icon}] {c['check']:<28} {c['status']:<10} {detail}")
        if c.get("fix"):
            print(f"       Fix: {c['fix']}")


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Apotheon memory layer health check")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output JSON")
    parser.add_argument("--fix", action="store_true", help="Auto-fix missing collections")
    args = parser.parse_args()

    checks = run_checks(fix=args.fix)

    if args.as_json:
        print(json.dumps(checks, indent=2))
    else:
        print("Memory layer health check:")
        print_table(checks)

    failed = [c for c in checks if c["status"] == "fail"]
    if failed:
        print(f"\n{len(failed)} check(s) failed.")
        return 1
    print("\nAll memory checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())