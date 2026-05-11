from __future__ import annotations

from .base import NormalizedListing, SourceAdapter, utc_now_iso


class EbayAdapter(SourceAdapter):
    source_id = "ebay"

    def normalize(self, payload: dict, *, lineage_run_id: str) -> NormalizedListing:
        selling_status = payload.get("sellingStatus", {})
        current_price = selling_status.get("currentPrice", {})
        return NormalizedListing(
            source_id=self.source_id,
            listing_id=str(payload["itemId"]),
            title=str(payload.get("title", "")),
            price_amount=float(current_price.get("value", 0.0)),
            price_currency=str(current_price.get("currencyId", "USD")),
            captured_at=utc_now_iso(),
            lineage_run_id=lineage_run_id,
            raw_payload=payload,
        )
