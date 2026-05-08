#!/usr/bin/env python3
"""
slack_connector.py — Slack Web API connector.

Authentication: Bot token (xoxb-...) via API key header.

Required secrets:
    slack-bot-token    xoxb-... Bot OAuth token

Optional secrets:
    slack-signing-secret   For webhook signature verification (not used here)
"""
from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from typing import Any

from base_connector import BaseConnector, resolve_secret
from auth.api_key_client import ApiKeyAuth, ApiKeyStyle

logger = logging.getLogger("connector.slack")

SLACK_API_BASE = "https://slack.com/api"


class SlackConnector(BaseConnector):
    """Slack Web API connector."""

    RATE_LIMIT_RPM = 50  # Slack Tier 3: ~50 RPM for most methods

    def _authenticate(self) -> None:
        token = resolve_secret("slack-bot-token")
        auth = ApiKeyAuth(token, style=ApiKeyStyle.BEARER)
        self._auth_headers = auth.auth_headers
        logger.info("Slack authenticated (token prefix: %s...)", token[:12])

    def health_check(self) -> bool:
        try:
            resp = self._request("GET", f"{SLACK_API_BASE}/auth.test")
            return resp.get("ok", False)
        except Exception as exc:
            logger.warning("Slack health check failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Internal helper: Slack returns 200 even on errors
    # ------------------------------------------------------------------

    def _slack_request(self, method: str, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        resp = self._request(method, f"{SLACK_API_BASE}/{endpoint}", **kwargs)
        if not resp.get("ok"):
            raise RuntimeError(f"Slack API error on {endpoint}: {resp.get('error', 'unknown')}")
        return resp

    # ------------------------------------------------------------------
    # Messaging
    # ------------------------------------------------------------------

    def post_message(
        self,
        channel: str,
        text: str,
        blocks: list[dict] | None = None,
        thread_ts: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"channel": channel, "text": text}
        if blocks:
            payload["blocks"] = blocks
        if thread_ts:
            payload["thread_ts"] = thread_ts
        return self._slack_request("POST", "chat.postMessage", payload=payload)

    def update_message(self, channel: str, ts: str, text: str) -> dict[str, Any]:
        return self._slack_request(
            "POST", "chat.update", payload={"channel": channel, "ts": ts, "text": text}
        )

    def delete_message(self, channel: str, ts: str) -> None:
        self._slack_request("POST", "chat.delete", payload={"channel": channel, "ts": ts})

    # ------------------------------------------------------------------
    # Channels
    # ------------------------------------------------------------------

    def list_channels(self, limit: int = 200) -> list[dict[str, Any]]:
        resp = self._slack_request(
            "GET", f"conversations.list?limit={limit}&types=public_channel,private_channel"
        )
        return resp.get("channels", [])

    def get_channel_history(self, channel: str, limit: int = 100) -> list[dict[str, Any]]:
        resp = self._slack_request("GET", f"conversations.history?channel={channel}&limit={limit}")
        return resp.get("messages", [])

    def join_channel(self, channel: str) -> None:
        self._slack_request("POST", "conversations.join", payload={"channel": channel})

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    def lookup_user_by_email(self, email: str) -> dict[str, Any]:
        resp = self._slack_request("GET", f"users.lookupByEmail?email={urllib.parse.quote(email)}")
        return resp.get("user", {})

    def get_user_info(self, user_id: str) -> dict[str, Any]:
        resp = self._slack_request("GET", f"users.info?user={user_id}")
        return resp.get("user", {})

    # ------------------------------------------------------------------
    # Files
    # ------------------------------------------------------------------

    def upload_file(self, channel: str, content: str, filename: str, title: str = "") -> dict:
        payload = {
            "channels": channel,
            "content": content,
            "filename": filename,
            "title": title or filename,
        }
        return self._slack_request("POST", "files.upload", payload=payload)