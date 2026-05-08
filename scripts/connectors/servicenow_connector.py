#!/usr/bin/env python3
"""
servicenow_connector.py — ServiceNow Table API connector.

Authentication: Basic auth (username + password) or OAuth 2.0.

Required secrets:
    servicenow-instance-url    e.g. https://mycompany.service-now.com
    servicenow-username
    servicenow-password
"""
from __future__ import annotations

import base64
import logging
from typing import Any

from base_connector import BaseConnector, resolve_secret

logger = logging.getLogger("connector.servicenow")


class ServiceNowConnector(BaseConnector):
    """ServiceNow Table API connector."""

    RATE_LIMIT_RPM = 60
    API_BASE = "/api/now/table"

    def _authenticate(self) -> None:
        instance_url = resolve_secret("servicenow-instance-url")
        username = resolve_secret("servicenow-username")
        password = resolve_secret("servicenow-password")

        self._instance_url = instance_url.rstrip("/")
        encoded = base64.b64encode(f"{username}:{password}".encode()).decode()
        self._auth_headers = {
            "Authorization": f"Basic {encoded}",
            "Accept": "application/json",
        }
        logger.info("ServiceNow authenticated (instance: %s)", self._instance_url)

    def _url(self, table: str, sys_id: str = "") -> str:
        base = f"{self._instance_url}{self.API_BASE}/{table}"
        return f"{base}/{sys_id}" if sys_id else base

    def health_check(self) -> bool:
        try:
            self._request("GET", f"{self._instance_url}/api/now/table/sys_user?sysparm_limit=1")
            return True
        except Exception as exc:
            logger.warning("ServiceNow health check failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Table API helpers
    # ------------------------------------------------------------------

    def get_records(
        self,
        table: str,
        query: str = "",
        fields: list[str] | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query a table with optional encoded query string."""
        url = self._url(table)
        params = [f"sysparm_limit={limit}"]
        if query:
            params.append(f"sysparm_query={query}")
        if fields:
            params.append(f"sysparm_fields={','.join(fields)}")
        full_url = f"{url}?{'&'.join(params)}"
        resp = self._request("GET", full_url)
        return resp.get("result", [])

    def get_record(self, table: str, sys_id: str) -> dict[str, Any]:
        resp = self._request("GET", self._url(table, sys_id))
        return resp.get("result", {})

    def create_record(self, table: str, fields: dict[str, Any]) -> dict[str, Any]:
        resp = self._request("POST", self._url(table), payload=fields)
        return resp.get("result", {})

    def update_record(self, table: str, sys_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        resp = self._request("PATCH", self._url(table, sys_id), payload=fields)
        return resp.get("result", {})

    # ------------------------------------------------------------------
    # Incident shortcuts
    # ------------------------------------------------------------------

    def get_incidents(self, state: str | None = None, limit: int = 100) -> list[dict]:
        query = f"state={state}" if state else ""
        return self.get_records("incident", query=query, limit=limit)

    def create_incident(
        self,
        short_description: str,
        urgency: int = 3,
        impact: int = 3,
        assignment_group: str = "",
    ) -> dict[str, Any]:
        fields: dict[str, Any] = {
            "short_description": short_description,
            "urgency": urgency,
            "impact": impact,
        }
        if assignment_group:
            fields["assignment_group"] = assignment_group
        return self.create_record("incident", fields)

    def get_change_requests(self, state: str | None = None) -> list[dict]:
        query = f"state={state}" if state else ""
        return self.get_records("change_request", query=query)