#!/usr/bin/env python3
"""
oauth2_client.py — OAuth 2.0 client credentials and authorization code flows.

Handles token acquisition, caching, and automatic refresh for connectors
that use OAuth 2.0 (Salesforce, HubSpot, Google, etc.).
"""
from __future__ import annotations

import base64
import json
import logging
import os
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

logger = logging.getLogger("oauth2_client")


@dataclass
class OAuth2Token:
    access_token: str
    expires_at: float  # Unix timestamp
    token_type: str = "Bearer"
    refresh_token: str = ""
    scope: str = ""

    @property
    def is_expired(self) -> bool:
        """Return True if token expires within the next 60 seconds."""
        return time.time() >= self.expires_at - 60

    @property
    def auth_header(self) -> str:
        return f"{self.token_type} {self.access_token}"


class OAuth2ClientCredentials:
    """
    OAuth 2.0 Client Credentials flow.

    Used by: Salesforce (JWT), Google (service account), HubSpot (private app).
    """

    def __init__(
        self,
        token_endpoint: str,
        client_id: str,
        client_secret: str,
        scope: str = "",
        extra_params: dict | None = None,
    ):
        self.token_endpoint = token_endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.extra_params = extra_params or {}
        self._token: OAuth2Token | None = None

    def get_token(self) -> OAuth2Token:
        """Return a valid access token, refreshing if expired."""
        if self._token is None or self._token.is_expired:
            self._token = self._fetch_token()
        return self._token

    def _fetch_token(self) -> OAuth2Token:
        params = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        if self.scope:
            params["scope"] = self.scope
        params.update(self.extra_params)

        data = urllib.parse.urlencode(params).encode()
        req = urllib.request.Request(
            self.token_endpoint,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read())

        expires_in = int(body.get("expires_in", 3600))
        return OAuth2Token(
            access_token=body["access_token"],
            expires_at=time.time() + expires_in,
            token_type=body.get("token_type", "Bearer"),
            refresh_token=body.get("refresh_token", ""),
            scope=body.get("scope", self.scope),
        )

    @property
    def auth_header(self) -> str:
        return self.get_token().auth_header


class OAuth2AuthorizationCode:
    """
    OAuth 2.0 Authorization Code flow with refresh token support.

    Used by: Salesforce (user auth), Intercom, Zendesk.
    """

    def __init__(
        self,
        token_endpoint: str,
        client_id: str,
        client_secret: str,
        refresh_token: str,
    ):
        self.token_endpoint = token_endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self._refresh_token = refresh_token
        self._token: OAuth2Token | None = None

    def get_token(self) -> OAuth2Token:
        if self._token is None or self._token.is_expired:
            self._token = self._refresh()
        return self._token

    def _refresh(self) -> OAuth2Token:
        params = {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        data = urllib.parse.urlencode(params).encode()
        req = urllib.request.Request(
            self.token_endpoint,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read())

        # Update refresh token if a new one was issued
        if "refresh_token" in body:
            self._refresh_token = body["refresh_token"]

        expires_in = int(body.get("expires_in", 3600))
        return OAuth2Token(
            access_token=body["access_token"],
            expires_at=time.time() + expires_in,
            token_type=body.get("token_type", "Bearer"),
            refresh_token=self._refresh_token,
        )

    @property
    def auth_header(self) -> str:
        return self.get_token().auth_header