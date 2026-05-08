#!/usr/bin/env python3
"""
mixpanel_connector.py — Mixpanel Data Export API connector.

Authentication: Service Account (Basic auth with username:secret).

Required secrets:
    mixpanel-service-account-username
    mixpanel-service-account-secret
    mixpanel-project-id
"""
from __future__ import annotations

import base64
import logging
import urllib.parse
from typing import Any

from base_connector import BaseConnector, resolve_secret

logger = logging.getLogger("connector.mixpanel")

MIXPANEL_DATA_BASE = "https://data.mixpanel.com/api/2.0"
MIXPANEL_API_BASE = "https://mixpanel.com/api/2.0"


class MixpanelConnector(BaseConnector):
    """Mixpanel Data Export and Query API connector."""

    RATE_LIMIT_RPM = 60

    def _authenticate(self) -> None:
        username = resolve_secret("mixpanel-service-account-username")
        secret = resolve_secret("mixpanel-service-account-secret")
        project_id = resolve_secret("mixpanel-project-id")

        encoded = base64.b64encode(f"{username}:{secret}".encode()).decode()
        self._auth_headers = {"Authorization": f"Basic {encoded}"}
        self._project_id = project_id
        logger.info("Mixpanel authenticated (project: %s)", project_id)

    def health_check(self) -> bool:
        try:
            self._request("GET", f"{MIXPANEL_API_BASE}/projects/{self._project_id}")
            return True
        except Exception as exc:
            logger.warning("Mixpanel health check failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def get_event_names(self) -> list[str]:
        resp = self._request("GET", f"{MIXPANEL_DATA_BASE}/events/names?type=general&project_id={self._project_id}")
        return resp if isinstance(resp, list) else []

    def get_event_totals(self, event: str, from_date: str, to_date: str, unit: str = "day") -> dict:
        """Get daily/weekly/monthly totals for an event."""
        params = urllib.parse.urlencode({
            "event": f'["{event}"]',
            "type": "general",
            "unit": unit,
            "from_date": from_date,
            "to_date": to_date,
            "project_id": self._project_id,
        })
        return self._request("GET", f"{MIXPANEL_DATA_BASE}/events?{params}")

    # ------------------------------------------------------------------
    # Funnels
    # ------------------------------------------------------------------

    def get_funnels(self) -> list[dict]:
        resp = self._request("GET", f"{MIXPANEL_DATA_BASE}/funnels/list?project_id={self._project_id}")
        return resp.get("results", []) if isinstance(resp, dict) else []

    def get_funnel(self, funnel_id: int, from_date: str, to_date: str) -> dict:
        params = urllib.parse.urlencode({
            "funnel_id": funnel_id,
            "from_date": from_date,
            "to_date": to_date,
            "project_id": self._project_id,
        })
        return self._request("GET", f"{MIXPANEL_DATA_BASE}/funnels?{params}")

    # ------------------------------------------------------------------
    # Retention
    # ------------------------------------------------------------------

    def get_retention(self, from_date: str, to_date: str, retention_type: str = "birth") -> dict:
        params = urllib.parse.urlencode({
            "from_date": from_date,
            "to_date": to_date,
            "retention_type": retention_type,
            "project_id": self._project_id,
        })
        return self._request("GET", f"{MIXPANEL_DATA_BASE}/retention?{params}")

    # ------------------------------------------------------------------
    # Segmentation (breakdown by property)
    # ------------------------------------------------------------------

    def segment_event(
        self,
        event: str,
        from_date: str,
        to_date: str,
        on: str,
        unit: str = "day",
    ) -> dict:
        """Break down an event by a user/event property."""
        params = urllib.parse.urlencode({
            "event": f'"{event}"',
            "from_date": from_date,
            "to_date": to_date,
            "on": f'properties["{on}"]',
            "unit": unit,
            "project_id": self._project_id,
        })
        return self._request("GET", f"{MIXPANEL_DATA_BASE}/segmentation?{params}")