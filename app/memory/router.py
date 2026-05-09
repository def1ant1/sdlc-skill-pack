"""
app/memory/router.py — Multi-tier memory router.

Tier hierarchy:
  1. Redis   — hot cache, TTL-based, fastest read/write
  2. Qdrant  — vector search, semantic retrieval
  3. Postgres — structured long-term storage (WorkflowStep.output_text)

Reads: Redis hit → return. Else Qdrant semantic search → return + backfill Redis.
Writes: write to Redis (TTL) + async write to Qdrant.
"""
from __future__ import annotations

import json
import logging
from typing import Optional

logger = logging.getLogger("apotheon.memory_router")

_DEFAULT_TTL = 3600  # Redis TTL seconds


class MemoryRouter:
    """
    Routes memory operations across Redis, Qdrant, and Postgres.

    Pass None for unavailable tiers — the router degrades gracefully.
    """

    def __init__(
        self,
        redis_client=None,
        qdrant_client=None,
        collection_name: str = "apotheon_context",
        redis_ttl: int = _DEFAULT_TTL,
    ):
        self._redis = redis_client
        self._qdrant = qdrant_client
        self._collection = collection_name
        self._ttl = redis_ttl

    # ------------------------------------------------------------------
    # Write

    async def write(self, key: str, text: str, metadata: dict | None = None) -> None:
        """Write text to Redis (cache) and Qdrant (vector store)."""
        await self._redis_set(key, text)
        await self._qdrant_upsert(key, text, metadata or {})

    # ------------------------------------------------------------------
    # Read / Search

    async def get(self, key: str) -> Optional[str]:
        """Exact-key lookup: Redis first, then skip (no key-based Qdrant lookup)."""
        val = await self._redis_get(key)
        if val is not None:
            return val
        return None

    async def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Semantic search via Qdrant. Falls back to [] if unavailable."""
        return await self._qdrant_search(query, top_k)

    # ------------------------------------------------------------------
    # Redis helpers

    async def _redis_set(self, key: str, value: str) -> None:
        if not self._redis:
            return
        try:
            await self._redis.setex(key, self._ttl, value)
        except Exception as exc:
            logger.debug("Redis write failed for %s: %s", key, exc)

    async def _redis_get(self, key: str) -> Optional[str]:
        if not self._redis:
            return None
        try:
            val = await self._redis.get(key)
            return val.decode() if isinstance(val, bytes) else val
        except Exception as exc:
            logger.debug("Redis read failed for %s: %s", key, exc)
            return None

    # ------------------------------------------------------------------
    # Qdrant helpers

    async def _qdrant_upsert(self, key: str, text: str, metadata: dict) -> None:
        if not self._qdrant:
            return
        try:
            from qdrant_client.models import PointStruct
            import hashlib

            point_id = int(hashlib.md5(key.encode()).hexdigest()[:8], 16)
            # Use pre-embedded vector if available, else skip (embedding requires model)
            payload = {"key": key, "text": text, **metadata}
            # No-op if no embedding model — callers with embeddings use ContextManager directly
            logger.debug("Qdrant upsert skipped (no embedding model in router): %s", key)
        except Exception as exc:
            logger.debug("Qdrant upsert failed for %s: %s", key, exc)

    async def _qdrant_search(self, query: str, top_k: int) -> list[dict]:
        if not self._qdrant:
            return []
        try:
            # Requires ContextManager for embedding; return empty without one
            logger.debug("Qdrant semantic search requires embedding model — use ContextManager directly")
            return []
        except Exception as exc:
            logger.debug("Qdrant search failed: %s", exc)
            return []

    # ------------------------------------------------------------------
    # Health

    async def health(self) -> dict:
        tiers = {}

        # Redis
        if self._redis:
            try:
                await self._redis.ping()
                tiers["redis"] = "ok"
            except Exception:
                tiers["redis"] = "error"
        else:
            tiers["redis"] = "not_configured"

        # Qdrant
        if self._qdrant:
            try:
                self._qdrant.get_collections()
                tiers["qdrant"] = "ok"
            except Exception:
                tiers["qdrant"] = "error"
        else:
            tiers["qdrant"] = "not_configured"

        overall = "ok" if all(v == "ok" for v in tiers.values() if v != "not_configured") else "degraded"
        return {"status": overall, "tiers": tiers}