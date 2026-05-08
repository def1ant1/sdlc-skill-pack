#!/usr/bin/env python3
"""
stripe_connector.py — Stripe API connector.

Authentication: Secret key (Bearer / Basic with key as username).

Required secrets:
    stripe-secret-key    sk_live_... or sk_test_...
"""
from __future__ import annotations

import base64
import logging
import urllib.parse
from typing import Any

from base_connector import BaseConnector, resolve_secret

logger = logging.getLogger("connector.stripe")

STRIPE_BASE = "https://api.stripe.com/v1"


class StripeConnector(BaseConnector):
    """Stripe API connector (Charges, Customers, Subscriptions, Invoices)."""

    RATE_LIMIT_RPM = 100
    # Stripe uses form-encoded POST bodies
    NON_RETRYABLE_STATUS_CODES = frozenset({400, 401, 402, 403, 404})

    def _authenticate(self) -> None:
        secret_key = resolve_secret("stripe-secret-key")
        encoded = base64.b64encode(f"{secret_key}:".encode()).decode()
        self._auth_headers = {"Authorization": f"Basic {encoded}"}
        self._is_live = not secret_key.startswith("sk_test_")
        logger.info("Stripe authenticated (mode: %s)", "live" if self._is_live else "test")

    def health_check(self) -> bool:
        try:
            self._request("GET", f"{STRIPE_BASE}/balance")
            return True
        except Exception as exc:
            logger.warning("Stripe health check failed: %s", exc)
            return False

    def _form_request(self, method: str, path: str, params: dict | None = None) -> dict:
        """Stripe uses form-encoded bodies for POST/DELETE, query strings for GET."""
        import urllib.request
        import json as _json

        url = f"{STRIPE_BASE}/{path.lstrip('/')}"
        headers = {**self._auth_headers}

        if method == "GET" and params:
            url += "?" + urllib.parse.urlencode(params, doseq=True)
            data = None
        elif params:
            data = urllib.parse.urlencode(params, doseq=True).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            data = None

        self._rate_limiter.acquire()
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        import urllib.error
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read()
                return _json.loads(body) if body else {}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")[:500]
            raise RuntimeError(f"Stripe HTTP {exc.code} {method} {url}: {body}") from exc

    # ------------------------------------------------------------------
    # Customers
    # ------------------------------------------------------------------

    def get_customers(self, limit: int = 100, email: str | None = None) -> list[dict]:
        params: dict = {"limit": limit}
        if email:
            params["email"] = email
        resp = self._form_request("GET", "customers", params)
        return resp.get("data", [])

    def create_customer(self, email: str, name: str = "", metadata: dict | None = None) -> dict:
        params: dict = {"email": email}
        if name:
            params["name"] = name
        if metadata:
            for k, v in metadata.items():
                params[f"metadata[{k}]"] = str(v)
        return self._form_request("POST", "customers", params)

    # ------------------------------------------------------------------
    # Subscriptions
    # ------------------------------------------------------------------

    def get_subscriptions(self, status: str = "active", limit: int = 100) -> list[dict]:
        resp = self._form_request("GET", "subscriptions", {"status": status, "limit": limit})
        return resp.get("data", [])

    def get_subscription(self, subscription_id: str) -> dict:
        return self._form_request("GET", f"subscriptions/{subscription_id}")

    def cancel_subscription(self, subscription_id: str) -> dict:
        return self._form_request("DELETE", f"subscriptions/{subscription_id}")

    # ------------------------------------------------------------------
    # Invoices
    # ------------------------------------------------------------------

    def get_invoices(self, customer_id: str | None = None, limit: int = 100) -> list[dict]:
        params: dict = {"limit": limit}
        if customer_id:
            params["customer"] = customer_id
        resp = self._form_request("GET", "invoices", params)
        return resp.get("data", [])

    def get_upcoming_invoice(self, customer_id: str) -> dict:
        return self._form_request("GET", "invoices/upcoming", {"customer": customer_id})

    # ------------------------------------------------------------------
    # Revenue metrics
    # ------------------------------------------------------------------

    def get_balance(self) -> dict:
        return self._form_request("GET", "balance")

    def get_mrr_snapshot(self) -> dict:
        """Approximate MRR from active subscription amounts."""
        subs = self.get_subscriptions(status="active", limit=100)
        mrr_cents = 0
        for sub in subs:
            items = sub.get("items", {}).get("data", [])
            for item in items:
                plan = item.get("plan", {})
                amount = plan.get("amount", 0)
                interval = plan.get("interval", "month")
                qty = item.get("quantity", 1)
                if interval == "year":
                    amount = amount // 12
                mrr_cents += amount * qty
        return {
            "mrr_cents": mrr_cents,
            "mrr_dollars": round(mrr_cents / 100, 2),
            "active_subscriptions": len(subs),
        }

    # ------------------------------------------------------------------
    # Charges
    # ------------------------------------------------------------------

    def get_charges(self, limit: int = 100, customer_id: str | None = None) -> list[dict]:
        params: dict = {"limit": limit}
        if customer_id:
            params["customer"] = customer_id
        resp = self._form_request("GET", "charges", params)
        return resp.get("data", [])