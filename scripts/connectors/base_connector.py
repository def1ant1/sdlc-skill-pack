#!/usr/bin/env python3
"""
base_connector.py — Abstract base class for Apotheon integration connectors.

Every connector (Salesforce, ServiceNow, GA4, Slack, etc.) extends BaseConnector
and implements:
  - _authenticate() → populates self._auth_headers
  - health_check() → returns bool
  - (domain-specific methods)

The base class handles:
  - Secret resolution (Vault → env var → .env fallback)
  - Rate limiting (token bucket via RateLimiter)
  - Retry with exponential backoff
  - Structured logging
"""
from __future__ import annotations

import json
import logging
import os
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class DryRunSideEffectBlocked(RuntimeError):
    """Raised when connector outbound calls are blocked in dry-run mode."""


def _dry_run_enabled() -> bool:
    return os.environ.get("APOTHEON_DRY_RUN", "").strip().lower() in {"1", "true", "yes", "on"}

# ---------------------------------------------------------------------------
# Secret resolution
# ---------------------------------------------------------------------------

def resolve_secret(secret_name: str) -> str:
    """
    Resolve a secret in priority order:
      1. HashiCorp Vault (if VAULT_ADDR and VAULT_TOKEN set)
      2. Environment variable APOTHEON_{SECRET_NAME_UPPER}
      3. Environment variable {SECRET_NAME_UPPER} (fallback)
      4. Raises EnvironmentError if not found
    """
    env_key = f"APOTHEON_{secret_name.upper().replace('-', '_')}"
    fallback_key = secret_name.upper().replace("-", "_")

    # Try Vault first
    vault_addr = os.environ.get("VAULT_ADDR", "")
    vault_token = os.environ.get("VAULT_TOKEN", "")
    if vault_addr and vault_token:
        try:
            return _resolve_from_vault(vault_addr, vault_token, secret_name)
        except Exception as exc:
            logger.debug("Vault lookup failed for %s: %s — falling back to env", secret_name, exc)

    # Try env vars
    value = os.environ.get(env_key) or os.environ.get(fallback_key)
    if value:
        return value

    raise EnvironmentError(
        f"Secret '{secret_name}' not found. Set env var '{env_key}' or configure Vault."
    )


def _resolve_from_vault(vault_addr: str, token: str, secret_name: str) -> str:
    path = f"secret/connectors/{secret_name}"
    req = urllib.request.Request(
        f"{vault_addr}/v1/{path}",
        headers={"X-Vault-Token": token},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read())
    return data["data"]["value"]


# ---------------------------------------------------------------------------
# Rate limiter (simple token bucket)
# ---------------------------------------------------------------------------

class RateLimiter:
    """Per-connector token bucket rate limiter."""

    def __init__(self, requests_per_minute: int):
        self._rpm = requests_per_minute
        self._tokens = float(requests_per_minute)
        self._last_refill = time.monotonic()
        self._interval = 60.0 / requests_per_minute

    def acquire(self) -> None:
        """Block until a request token is available."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._rpm, self._tokens + elapsed * (self._rpm / 60.0))
        self._last_refill = now

        if self._tokens < 1.0:
            sleep_time = (1.0 - self._tokens) * self._interval
            logger.debug("Rate limit: sleeping %.2fs", sleep_time)
            time.sleep(sleep_time)
            self._tokens = 0.0
        else:
            self._tokens -= 1.0

    def handle_429(self, retry_after_seconds: float = 60.0) -> None:
        """Drain tokens and sleep after a 429 response."""
        self._tokens = 0.0
        logger.warning("Rate limited (429): sleeping %.0fs", retry_after_seconds)
        time.sleep(retry_after_seconds)


# ---------------------------------------------------------------------------
# Base connector
# ---------------------------------------------------------------------------

class BaseConnector(ABC):
    """Abstract base class for all Apotheon integration connectors."""

    #: Override in subclass — requests per minute for this connector
    RATE_LIMIT_RPM: int = 60
    #: Retry settings
    MAX_RETRIES: int = 3
    INITIAL_BACKOFF_SECONDS: float = 1.0
    BACKOFF_MULTIPLIER: float = 2.0
    MAX_BACKOFF_SECONDS: float = 60.0
    #: HTTP status codes that are retryable
    RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({429, 502, 503, 504})
    #: HTTP status codes that are NOT retryable (client errors)
    NON_RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({400, 401, 403, 404, 422})

    def __init__(self):
        self._auth_headers: dict[str, str] = {}
        self._rate_limiter = RateLimiter(self.RATE_LIMIT_RPM)
        self._authenticated = False
        self.logger = logging.getLogger(f"connector.{self.__class__.__name__.lower()}")

    @abstractmethod
    def _authenticate(self) -> None:
        """Populate self._auth_headers. Called lazily on first request."""

    @abstractmethod
    def health_check(self) -> bool:
        """Return True if the connector can reach the remote service."""

    def _ensure_authenticated(self) -> None:
        if not self._authenticated:
            self._authenticate()
            self._authenticated = True

    def _request(
        self,
        method: str,
        url: str,
        payload: dict | None = None,
        extra_headers: dict[str, str] | None = None,
        timeout: int = 30,
    ) -> dict[str, Any]:
        """
        Execute an HTTP request with rate limiting, retry, and error handling.

        Returns the parsed JSON response body.
        Raises RuntimeError on non-retryable errors.
        """
        if _dry_run_enabled():
            raise DryRunSideEffectBlocked(
                f"Outbound connector call blocked during dry-run: {method} {url}"
            )

        self._ensure_authenticated()
        self._rate_limiter.acquire()

        headers = {"Content-Type": "application/json", **self._auth_headers}
        if extra_headers:
            headers.update(extra_headers)

        data = json.dumps(payload).encode() if payload is not None else None
        backoff = self.INITIAL_BACKOFF_SECONDS

        for attempt in range(1, self.MAX_RETRIES + 2):
            try:
                req = urllib.request.Request(url, data=data, headers=headers, method=method)
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    body = resp.read()
                    return json.loads(body) if body else {}

            except urllib.error.HTTPError as exc:
                status = exc.code

                if status in self.NON_RETRYABLE_STATUS_CODES:
                    error_body = exc.read().decode(errors="replace")
                    raise RuntimeError(
                        f"HTTP {status} {method} {url}: {error_body}"
                    ) from exc

                if status == 429:
                    retry_after = float(exc.headers.get("Retry-After", backoff))
                    self._rate_limiter.handle_429(retry_after)
                    continue

                if status in self.RETRYABLE_STATUS_CODES and attempt <= self.MAX_RETRIES:
                    self.logger.warning(
                        "HTTP %s on attempt %d/%d — retrying in %.1fs",
                        status, attempt, self.MAX_RETRIES, backoff,
                    )
                    time.sleep(backoff)
                    backoff = min(backoff * self.BACKOFF_MULTIPLIER, self.MAX_BACKOFF_SECONDS)
                    continue

                raise RuntimeError(f"HTTP {status} {method} {url}") from exc

            except OSError as exc:
                if attempt <= self.MAX_RETRIES:
                    self.logger.warning(
                        "Network error on attempt %d/%d: %s — retrying in %.1fs",
                        attempt, self.MAX_RETRIES, exc, backoff,
                    )
                    time.sleep(backoff)
                    backoff = min(backoff * self.BACKOFF_MULTIPLIER, self.MAX_BACKOFF_SECONDS)
                    continue
                raise

        raise RuntimeError(f"All {self.MAX_RETRIES} retries exhausted for {method} {url}")