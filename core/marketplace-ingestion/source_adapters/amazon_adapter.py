from __future__ import annotations

from .base import NormalizedListing, SourceAdapter, utc_now_iso


class AmazonAdapter(SourceAdapter):
    source_id = "amazon"

    def normalize(self, payload: dict, *, lineage_run_id: str) -> NormalizedListing:
        offer = payload.get("offer", {})
        price = offer.get("price", {})
        return NormalizedListing(
            source_id=self.source_id,
            listing_id=str(payload["asin"]),
            title=str(payload.get("title", "")),
            price_amount=float(price.get("amount", 0.0)),
            price_currency=str(price.get("currency", "USD")),
            captured_at=utc_now_iso(),
            lineage_run_id=lineage_run_id,
            raw_payload=payload,
        )
