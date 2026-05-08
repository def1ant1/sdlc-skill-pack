#!/usr/bin/env python3
"""
api_key_client.py — API key authentication for connectors.

Supports three injection styles:
  - Header (most common): Authorization: Bearer <key> or X-Api-Key: <key>
  - Query parameter:       ?api_key=<key>
  - Basic auth:            Authorization: Basic base64(key:)
"""
from __future__ import annotations

import base64
from enum import Enum


class ApiKeyStyle(str, Enum):
    HEADER = "header"
    BEARER = "bearer"
    QUERY = "query"
    BASIC = "basic"


class ApiKeyAuth:
    """
    API key credential holder.

    Args:
        api_key:        The raw API key string.
        style:          Injection style (header/bearer/query/basic).
        header_name:    Header name when style=HEADER (default: X-Api-Key).
        query_param:    Query param name when style=QUERY (default: api_key).
    """

    def __init__(
        self,
        api_key: str,
        style: ApiKeyStyle = ApiKeyStyle.BEARER,
        header_name: str = "X-Api-Key",
        query_param: str = "api_key",
    ):
        if not api_key:
            raise ValueError("api_key must not be empty")
        self._key = api_key
        self.style = style
        self.header_name = header_name
        self.query_param = query_param

    # ------------------------------------------------------------------
    # Header-based injection
    # ------------------------------------------------------------------

    @property
    def auth_headers(self) -> dict[str, str]:
        """Return a dict of HTTP headers to inject for header/bearer/basic styles."""
        if self.style == ApiKeyStyle.BEARER:
            return {"Authorization": f"Bearer {self._key}"}
        if self.style == ApiKeyStyle.HEADER:
            return {self.header_name: self._key}
        if self.style == ApiKeyStyle.BASIC:
            encoded = base64.b64encode(f"{self._key}:".encode()).decode()
            return {"Authorization": f"Basic {encoded}"}
        # QUERY style — no headers
        return {}

    # ------------------------------------------------------------------
    # Query-string injection
    # ------------------------------------------------------------------

    def inject_query_param(self, url: str) -> str:
        """Append the API key as a query parameter (only for style=QUERY)."""
        if self.style != ApiKeyStyle.QUERY:
            return url
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}{self.query_param}={self._key}"