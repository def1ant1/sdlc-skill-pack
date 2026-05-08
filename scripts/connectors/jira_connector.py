#!/usr/bin/env python3
"""
jira_connector.py — Jira Cloud REST API v3 connector.

Authentication: Basic auth with API token (email + token).

Required secrets:
    jira-base-url      e.g. https://myorg.atlassian.net
    jira-email         Atlassian account email
    jira-api-token     Jira API token (not password)
"""
from __future__ import annotations

import base64
import logging
from typing import Any

from base_connector import BaseConnector, resolve_secret

logger = logging.getLogger("connector.jira")


class JiraConnector(BaseConnector):
    """Jira Cloud REST API v3 connector."""

    RATE_LIMIT_RPM = 60

    def _authenticate(self) -> None:
        base_url = resolve_secret("jira-base-url")
        email = resolve_secret("jira-email")
        api_token = resolve_secret("jira-api-token")

        self._base_url = f"{base_url.rstrip('/')}/rest/api/3"
        encoded = base64.b64encode(f"{email}:{api_token}".encode()).decode()
        self._auth_headers = {
            "Authorization": f"Basic {encoded}",
            "Accept": "application/json",
        }
        logger.info("Jira authenticated (host: %s)", base_url)

    def health_check(self) -> bool:
        try:
            self._request("GET", f"{self._base_url}/myself")
            return True
        except Exception as exc:
            logger.warning("Jira health check failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Issues
    # ------------------------------------------------------------------

    def get_issue(self, issue_key: str) -> dict[str, Any]:
        return self._request("GET", f"{self._base_url}/issue/{issue_key}")

    def search_issues(
        self,
        jql: str,
        fields: list[str] | None = None,
        max_results: int = 100,
        start_at: int = 0,
    ) -> dict[str, Any]:
        """Execute a JQL search and return the full response (includes total)."""
        payload: dict[str, Any] = {
            "jql": jql,
            "maxResults": max_results,
            "startAt": start_at,
        }
        if fields:
            payload["fields"] = fields
        return self._request("POST", f"{self._base_url}/issue/search", payload=payload)

    def search_all(self, jql: str, fields: list[str] | None = None) -> list[dict[str, Any]]:
        """Paginate through all results for a JQL query."""
        issues: list[dict] = []
        start = 0
        page_size = 100
        while True:
            resp = self.search_issues(jql, fields=fields, max_results=page_size, start_at=start)
            batch = resp.get("issues", [])
            issues.extend(batch)
            total = resp.get("total", 0)
            start += len(batch)
            if start >= total or not batch:
                break
        return issues

    def create_issue(
        self,
        project_key: str,
        summary: str,
        issue_type: str = "Task",
        description: str = "",
        assignee_account_id: str | None = None,
        labels: list[str] | None = None,
        priority: str | None = None,
    ) -> dict[str, Any]:
        fields: dict[str, Any] = {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type},
        }
        if description:
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}],
            }
        if assignee_account_id:
            fields["assignee"] = {"accountId": assignee_account_id}
        if labels:
            fields["labels"] = labels
        if priority:
            fields["priority"] = {"name": priority}

        return self._request("POST", f"{self._base_url}/issue", payload={"fields": fields})

    def update_issue(self, issue_key: str, fields: dict[str, Any]) -> None:
        self._request("PUT", f"{self._base_url}/issue/{issue_key}", payload={"fields": fields})

    def transition_issue(self, issue_key: str, transition_id: str) -> None:
        self._request(
            "POST",
            f"{self._base_url}/issue/{issue_key}/transitions",
            payload={"transition": {"id": transition_id}},
        )

    def add_comment(self, issue_key: str, body_text: str) -> dict[str, Any]:
        comment_body = {
            "type": "doc",
            "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": body_text}]}],
        }
        return self._request(
            "POST",
            f"{self._base_url}/issue/{issue_key}/comment",
            payload={"body": comment_body},
        )

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------

    def get_projects(self) -> list[dict[str, Any]]:
        resp = self._request("GET", f"{self._base_url}/project/search")
        return resp.get("values", [])

    def get_transitions(self, issue_key: str) -> list[dict[str, Any]]:
        resp = self._request("GET", f"{self._base_url}/issue/{issue_key}/transitions")
        return resp.get("transitions", [])