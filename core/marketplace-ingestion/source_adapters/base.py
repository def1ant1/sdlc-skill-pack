from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol


@dataclass(slots=True)
class NormalizedListing:
    source_id: str
    listing_id: str
    title: str
    price_amount: float
    price_currency: str
    captured_at: str
    lineage_run_id: str
    raw_payload: dict[str, Any]


class SourceAdapter(Protocol):
    source_id: str

    def normalize(self, payload: dict[str, Any], *, lineage_run_id: str) -> NormalizedListing:
        ...


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
