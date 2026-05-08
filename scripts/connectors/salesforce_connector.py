#!/usr/bin/env python3
"""
salesforce_connector.py — Salesforce REST API connector.

Authentication: OAuth 2.0 Client Credentials (Connected App).

Required secrets (resolve_secret keys):
    salesforce-instance-url    e.g. https://myorg.my.salesforce.com
    salesforce-client-id       Connected App consumer key
    salesforce-client-secret   Connected App consumer secret

Environment variable overrides:
    APOTHEON_SALESFORCE_INSTANCE_URL
    APOTHEON_SALESFORCE_CLIENT_ID
    APOTHEON_SALESFORCE_CLIENT_SECRET
"""
from __future__ import annotations

import logging
from typing import Any

from base_connector import BaseConnector, resolve_secret
from auth.oauth2_client import OAuth2ClientCredentials

logger = logging.getLogger("connector.salesforce")


class SalesforceConnector(BaseConnector):
    """Salesforce REST API connector (API v59.0)."""

    RATE_LIMIT_RPM = 100
    API_VERSION = "v59.0"

    def _authenticate(self) -> None:
        instance_url = resolve_secret("salesforce-instance-url")
        client_id = resolve_secret("salesforce-client-id")
        client_secret = resolve_secret("salesforce-client-secret")

        self._instance_url = instance_url.rstrip("/")
        token_endpoint = f"{self._instance_url}/services/oauth2/token"

        self._oauth = OAuth2ClientCredentials(
            token_endpoint=token_endpoint,
            client_id=client_id,
            client_secret=client_secret,
        )
        token = self._oauth.get_token()
        self._auth_headers = {"Authorization": token.auth_header}
        logger.info("Salesforce authenticated (instance: %s)", self._instance_url)

    def _base_url(self) -> str:
        return f"{self._instance_url}/services/data/{self.API_VERSION}"

    def health_check(self) -> bool:
        try:
            self._request("GET", f"{self._base_url()}/limits")
            return True
        except Exception as exc:
            logger.warning("Salesforce health check failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # SOQL query
    # ------------------------------------------------------------------

    def query(self, soql: str) -> list[dict[str, Any]]:
        """Execute a SOQL query and return all records (handles pagination)."""
        url = f"{self._base_url()}/query"
        # Pass SOQL as query param by appending it; override _request for GET params
        encoded = soql.replace(" ", "+")
        records: list[dict] = []
        next_url: str | None = f"{url}?q={encoded}"

        while next_url:
            # Build full URL for paginated requests
            if next_url.startswith("/"):
                next_url = f"{self._instance_url}{next_url}"
            resp = self._request("GET", next_url)
            records.extend(resp.get("records", []))
            next_records_url = resp.get("nextRecordsUrl")
            next_url = next_records_url if next_records_url else None

        return records

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------

    def get_record(self, sobject: str, record_id: str) -> dict[str, Any]:
        return self._request("GET", f"{self._base_url()}/sobjects/{sobject}/{record_id}")

    def create_record(self, sobject: str, fields: dict[str, Any]) -> str:
        """Create a record and return its new ID."""
        resp = self._request("POST", f"{self._base_url()}/sobjects/{sobject}", payload=fields)
        return resp["id"]

    def update_record(self, sobject: str, record_id: str, fields: dict[str, Any]) -> None:
        self._request("PATCH", f"{self._base_url()}/sobjects/{sobject}/{record_id}", payload=fields)

    def delete_record(self, sobject: str, record_id: str) -> None:
        self._request("DELETE", f"{self._base_url()}/sobjects/{sobject}/{record_id}")

    # ------------------------------------------------------------------
    # Common object shortcuts
    # ------------------------------------------------------------------

    def get_opportunities(self, stage: str | None = None) -> list[dict]:
        where = f"WHERE StageName = '{stage}'" if stage else ""
        return self.query(
            f"SELECT Id, Name, StageName, Amount, CloseDate, AccountId FROM Opportunity {where}"
        )

    def get_accounts(self, limit: int = 200) -> list[dict]:
        return self.query(
            f"SELECT Id, Name, Industry, AnnualRevenue, OwnerId FROM Account LIMIT {limit}"
        )