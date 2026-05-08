#!/usr/bin/env python3
"""
hubspot_connector.py — HubSpot CRM API v3 connector.

Authentication: Private App token (Bearer).

Required secrets:
    hubspot-access-token    HubSpot Private App access token
"""
from __future__ import annotations

import logging
from typing import Any

from base_connector import BaseConnector, resolve_secret
from auth.api_key_client import ApiKeyAuth, ApiKeyStyle

logger = logging.getLogger("connector.hubspot")

HUBSPOT_BASE = "https://api.hubapi.com"


class HubSpotConnector(BaseConnector):
    """HubSpot CRM API v3 connector."""

    RATE_LIMIT_RPM = 100

    def _authenticate(self) -> None:
        token = resolve_secret("hubspot-access-token")
        auth = ApiKeyAuth(token, style=ApiKeyStyle.BEARER)
        self._auth_headers = auth.auth_headers
        logger.info("HubSpot authenticated")

    def health_check(self) -> bool:
        try:
            self._request("GET", f"{HUBSPOT_BASE}/crm/v3/objects/contacts?limit=1")
            return True
        except Exception as exc:
            logger.warning("HubSpot health check failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Contacts
    # ------------------------------------------------------------------

    def get_contacts(self, limit: int = 100, properties: list[str] | None = None) -> list[dict]:
        props = ",".join(properties or ["firstname", "lastname", "email", "company"])
        resp = self._request("GET", f"{HUBSPOT_BASE}/crm/v3/objects/contacts?limit={limit}&properties={props}")
        return resp.get("results", [])

    def create_contact(self, email: str, firstname: str = "", lastname: str = "", **extra: Any) -> dict:
        properties = {"email": email, "firstname": firstname, "lastname": lastname, **extra}
        return self._request("POST", f"{HUBSPOT_BASE}/crm/v3/objects/contacts", payload={"properties": properties})

    def update_contact(self, contact_id: str, properties: dict[str, Any]) -> dict:
        return self._request("PATCH", f"{HUBSPOT_BASE}/crm/v3/objects/contacts/{contact_id}", payload={"properties": properties})

    def search_contacts(self, filter_groups: list[dict], limit: int = 100) -> list[dict]:
        payload = {"filterGroups": filter_groups, "limit": limit}
        resp = self._request("POST", f"{HUBSPOT_BASE}/crm/v3/objects/contacts/search", payload=payload)
        return resp.get("results", [])

    # ------------------------------------------------------------------
    # Deals
    # ------------------------------------------------------------------

    def get_deals(self, limit: int = 100, properties: list[str] | None = None) -> list[dict]:
        props = ",".join(properties or ["dealname", "amount", "dealstage", "closedate", "pipeline"])
        resp = self._request("GET", f"{HUBSPOT_BASE}/crm/v3/objects/deals?limit={limit}&properties={props}")
        return resp.get("results", [])

    def create_deal(self, name: str, amount: float, stage: str, pipeline: str = "default", **extra: Any) -> dict:
        properties = {
            "dealname": name,
            "amount": str(amount),
            "dealstage": stage,
            "pipeline": pipeline,
            **extra,
        }
        return self._request("POST", f"{HUBSPOT_BASE}/crm/v3/objects/deals", payload={"properties": properties})

    def get_deal_pipeline_stages(self, pipeline_id: str = "default") -> list[dict]:
        resp = self._request("GET", f"{HUBSPOT_BASE}/crm/v3/pipelines/deals/{pipeline_id}/stages")
        return resp.get("results", [])

    # ------------------------------------------------------------------
    # Companies
    # ------------------------------------------------------------------

    def get_companies(self, limit: int = 100) -> list[dict]:
        resp = self._request("GET", f"{HUBSPOT_BASE}/crm/v3/objects/companies?limit={limit}&properties=name,domain,industry,annualrevenue")
        return resp.get("results", [])

    # ------------------------------------------------------------------
    # Engagement / Activities
    # ------------------------------------------------------------------

    def get_engagements(self, limit: int = 100) -> list[dict]:
        resp = self._request("GET", f"{HUBSPOT_BASE}/engagements/v1/engagements/paged?limit={limit}")
        return resp.get("results", [])