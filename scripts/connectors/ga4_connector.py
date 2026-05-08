#!/usr/bin/env python3
"""
ga4_connector.py — Google Analytics 4 Data API connector.

Authentication: OAuth 2.0 Client Credentials via Google service account.

Required secrets:
    ga4-property-id      GA4 property ID (numeric, e.g. 123456789)
    ga4-client-email     Service account email
    ga4-private-key      Service account private key (PEM, base64-encoded in secret)

Note: Google uses JWT-based service account auth. This implementation uses
the OAuth 2.0 token endpoint with a signed JWT assertion (RFC 7523).
For simplicity, requires google-auth library if available; falls back to
a clear error message if not installed.
"""
from __future__ import annotations

import json
import logging
import os
import urllib.request
from typing import Any

from base_connector import BaseConnector, resolve_secret

logger = logging.getLogger("connector.ga4")

GA4_SCOPE = "https://www.googleapis.com/auth/analytics.readonly"
GA4_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GA4_DATA_API_BASE = "https://analyticsdata.googleapis.com/v1beta"


class GA4Connector(BaseConnector):
    """Google Analytics 4 Data API connector (runReport, batchRunReports)."""

    RATE_LIMIT_RPM = 60

    def _authenticate(self) -> None:
        try:
            import google.oauth2.service_account as sa
            import google.auth.transport.requests as gtr
        except ImportError:
            raise RuntimeError(
                "google-auth package required for GA4 connector. "
                "Install: pip install google-auth"
            )

        property_id = resolve_secret("ga4-property-id")
        client_email = resolve_secret("ga4-client-email")
        private_key_b64 = resolve_secret("ga4-private-key")

        import base64
        private_key = base64.b64decode(private_key_b64).decode()

        info = {
            "type": "service_account",
            "client_email": client_email,
            "private_key": private_key,
            "token_uri": GA4_TOKEN_ENDPOINT,
        }
        creds = sa.Credentials.from_service_account_info(info, scopes=[GA4_SCOPE])
        creds.refresh(gtr.Request())

        self._property_id = property_id
        self._auth_headers = {"Authorization": f"Bearer {creds.token}"}
        logger.info("GA4 authenticated (property: %s)", property_id)

    def health_check(self) -> bool:
        try:
            # Minimal metadata call
            url = f"{GA4_DATA_API_BASE}/properties/{self._property_id}/metadata"
            self._request("GET", url)
            return True
        except Exception as exc:
            logger.warning("GA4 health check failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Report runner
    # ------------------------------------------------------------------

    def run_report(
        self,
        date_ranges: list[dict],
        dimensions: list[str],
        metrics: list[str],
        dimension_filter: dict | None = None,
        limit: int = 10000,
    ) -> dict[str, Any]:
        """
        Run a GA4 Data API report.

        Args:
            date_ranges: list of {"startDate": "YYYY-MM-DD", "endDate": "YYYY-MM-DD"}
            dimensions:  list of dimension names e.g. ["date", "sessionSource"]
            metrics:     list of metric names e.g. ["sessions", "conversions"]
            dimension_filter: optional GA4 FilterExpression dict
            limit:       row limit (default 10000)

        Returns raw API response dict with rows, dimensionHeaders, metricHeaders.
        """
        url = f"{GA4_DATA_API_BASE}/properties/{self._property_id}:runReport"
        payload: dict[str, Any] = {
            "dateRanges": date_ranges,
            "dimensions": [{"name": d} for d in dimensions],
            "metrics": [{"name": m} for m in metrics],
            "limit": limit,
        }
        if dimension_filter:
            payload["dimensionFilter"] = dimension_filter

        return self._request("POST", url, payload=payload)

    # ------------------------------------------------------------------
    # Common report shortcuts
    # ------------------------------------------------------------------

    def sessions_by_channel(self, start_date: str, end_date: str) -> dict[str, Any]:
        return self.run_report(
            date_ranges=[{"startDate": start_date, "endDate": end_date}],
            dimensions=["sessionDefaultChannelGroup"],
            metrics=["sessions", "engagedSessions", "conversions"],
        )

    def top_pages(self, start_date: str, end_date: str, limit: int = 50) -> dict[str, Any]:
        return self.run_report(
            date_ranges=[{"startDate": start_date, "endDate": end_date}],
            dimensions=["pagePath", "pageTitle"],
            metrics=["screenPageViews", "averageSessionDuration", "bounceRate"],
            limit=limit,
        )

    def event_counts(self, start_date: str, end_date: str) -> dict[str, Any]:
        return self.run_report(
            date_ranges=[{"startDate": start_date, "endDate": end_date}],
            dimensions=["eventName"],
            metrics=["eventCount", "eventCountPerUser"],
        )