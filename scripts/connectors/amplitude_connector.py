#!/usr/bin/env python3
"""
amplitude_connector.py — Amplitude Analytics API connector.

Authentication: API Key + Secret Key (Basic auth).

Required secrets:
    amplitude-api-key
    amplitude-secret-key
"""
from __future__ import annotations

import base64
import logging
import urllib.parse
from typing import Any

from base_connector import BaseConnector, resolve_secret

logger = logging.getLogger("connector.amplitude")

AMPLITUDE_BASE = "https://amplitude.com/api/2"


class AmplitudeConnector(BaseConnector):
    """Amplitude Analytics API connector (Dashboard REST API v2)."""

    RATE_LIMIT_RPM = 30  # Amplitude is rate-limited aggressively

    def _authenticate(self) -> None:
        api_key = resolve_secret("amplitude-api-key")
        secret_key = resolve_secret("amplitude-secret-key")

        encoded = base64.b64encode(f"{api_key}:{secret_key}".encode()).decode()
        self._auth_headers = {"Authorization": f"Basic {encoded}"}
        logger.info("Amplitude authenticated")

    def health_check(self) -> bool:
        try:
            # Use events/segmentation as a health probe with minimal date range
            import datetime
            today = datetime.date.today().isoformat()
            yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
            self.get_event_segmentation(event_type="Any Event", start=yesterday, end=today)
            return True
        except Exception as exc:
            logger.warning("Amplitude health check failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Event Segmentation
    # ------------------------------------------------------------------

    def get_event_segmentation(
        self,
        event_type: str,
        start: str,
        end: str,
        m: str = "totals",
        i: int = 1,
        limit: int = 100,
    ) -> dict:
        """
        Query event segmentation.

        Args:
            event_type: Event name or "Any Event"
            start: Start date YYYY-MM-DD
            end: End date YYYY-MM-DD
            m: Metric (totals | uniques | pct_dau | average)
            i: Interval: 1 = daily, 7 = weekly, 30 = monthly
        """
        import json
        event_filter = json.dumps([{"event_type": event_type}])
        params = urllib.parse.urlencode({
            "e": event_filter,
            "start": start,
            "end": end,
            "m": m,
            "i": i,
            "limit": limit,
        })
        return self._request("GET", f"{AMPLITUDE_BASE}/events/segmentation?{params}")

    # ------------------------------------------------------------------
    # Funnels
    # ------------------------------------------------------------------

    def get_funnel(
        self,
        events: list[str],
        start: str,
        end: str,
        conversion_window: int = 7,
    ) -> dict:
        """
        Compute funnel conversion across a list of event names.

        Args:
            events: Ordered list of event names defining the funnel steps
            start: Start date YYYY-MM-DD
            end: End date YYYY-MM-DD
            conversion_window: Days to complete funnel
        """
        import json
        funnel_events = json.dumps([{"event_type": e} for e in events])
        params = urllib.parse.urlencode({
            "e": funnel_events,
            "start": start,
            "end": end,
            "conversion_window": conversion_window,
        })
        return self._request("GET", f"{AMPLITUDE_BASE}/funnels?{params}")

    # ------------------------------------------------------------------
    # Retention
    # ------------------------------------------------------------------

    def get_retention(self, start: str, end: str, retention_type: str = "n-day") -> dict:
        params = urllib.parse.urlencode({
            "start": start,
            "end": end,
            "retention_type": retention_type,
        })
        return self._request("GET", f"{AMPLITUDE_BASE}/retention?{params}")

    # ------------------------------------------------------------------
    # User Activity
    # ------------------------------------------------------------------

    def get_user_activity(self, user_id: str) -> dict:
        params = urllib.parse.urlencode({"user": user_id})
        return self._request("GET", f"{AMPLITUDE_BASE}/useractivity?{params}")

    def get_active_users(self, start: str, end: str, m: str = "active") -> dict:
        """m: active | new | resurrected | dormant"""
        params = urllib.parse.urlencode({"start": start, "end": end, "m": m})
        return self._request("GET", f"{AMPLITUDE_BASE}/users?{params}")