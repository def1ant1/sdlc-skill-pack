"""
app/connectors/vault_client.py — HashiCorp Vault secret retrieval.

Reads secrets from Vault KV v2 using a token or AppRole auth.
Caches leases in-process to avoid redundant Vault calls.

Required env vars:
  VAULT_ADDR        — e.g. http://vault:8200
  VAULT_TOKEN       — static token (or use AppRole below)
  VAULT_ROLE_ID     — AppRole role_id  (if using AppRole)
  VAULT_SECRET_ID   — AppRole secret_id
  VAULT_SECRET_PATH_PREFIX — default "secret/data/apotheon"
"""
from __future__ import annotations

import logging
import os
import time
from typing import Optional

logger = logging.getLogger("apotheon.vault")

VAULT_ADDR = os.environ.get("VAULT_ADDR", "http://vault:8200")
VAULT_TOKEN = os.environ.get("VAULT_TOKEN", "")
VAULT_ROLE_ID = os.environ.get("VAULT_ROLE_ID", "")
VAULT_SECRET_ID = os.environ.get("VAULT_SECRET_ID", "")
VAULT_SECRET_PATH_PREFIX = os.environ.get("VAULT_SECRET_PATH_PREFIX", "secret/data/apotheon")

_lease_cache: dict[str, tuple[dict, float]] = {}  # path -> (data, expires_at)
_LEASE_TTL = 300  # seconds


class VaultClient:
    """Simple synchronous Vault KV v2 client with in-process lease caching."""

    def __init__(
        self,
        addr: str = VAULT_ADDR,
        token: str = VAULT_TOKEN,
        role_id: str = VAULT_ROLE_ID,
        secret_id: str = VAULT_SECRET_ID,
    ):
        self._addr = addr.rstrip("/")
        self._token = token
        self._role_id = role_id
        self._secret_id = secret_id
        self._session_token: Optional[str] = None

    # ------------------------------------------------------------------

    def get_secret(self, path: str, key: Optional[str] = None) -> Optional[str]:
        """
        Retrieve a secret from Vault KV v2.

        Args:
            path: relative path under VAULT_SECRET_PATH_PREFIX, e.g. "github"
            key: specific key within the secret data dict; if None returns first value

        Returns:
            secret string, or None if unavailable
        """
        full_path = f"{VAULT_SECRET_PATH_PREFIX}/{path}"
        data = self._read_kv(full_path)
        if not data:
            return None
        if key:
            return data.get(key)
        return next(iter(data.values()), None) if data else None

    def _read_kv(self, full_path: str) -> Optional[dict]:
        """Read KV v2 secret, using cache if still valid."""
        cached, expires = _lease_cache.get(full_path, ({}, 0.0))
        if cached and time.time() < expires:
            return cached

        token = self._ensure_token()
        if not token:
            logger.warning("Vault: no auth token available — secret unavailable")
            return None

        try:
            import urllib.request
            import json

            url = f"{self._addr}/v1/{full_path}"
            req = urllib.request.Request(url, headers={"X-Vault-Token": token})
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = json.loads(resp.read())
                secret_data = body.get("data", {}).get("data", {})
                _lease_cache[full_path] = (secret_data, time.time() + _LEASE_TTL)
                return secret_data
        except Exception as exc:
            logger.warning("Vault read failed for %s: %s", full_path, exc)
            return None

    def _ensure_token(self) -> Optional[str]:
        if self._token:
            return self._token
        if self._session_token:
            return self._session_token
        if self._role_id and self._secret_id:
            return self._approle_login()
        return None

    def _approle_login(self) -> Optional[str]:
        try:
            import urllib.request
            import json

            payload = json.dumps({
                "role_id": self._role_id,
                "secret_id": self._secret_id,
            }).encode()
            url = f"{self._addr}/v1/auth/approle/login"
            req = urllib.request.Request(url, data=payload, method="POST",
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = json.loads(resp.read())
                self._session_token = body["auth"]["client_token"]
                logger.info("Vault AppRole login succeeded")
                return self._session_token
        except Exception as exc:
            logger.warning("Vault AppRole login failed: %s", exc)
            return None


# Module-level singleton — lazy-initialized
_client: Optional[VaultClient] = None


def get_vault_client() -> VaultClient:
    global _client
    if _client is None:
        _client = VaultClient()
    return _client