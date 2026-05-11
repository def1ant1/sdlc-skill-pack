from __future__ import annotations

import logging

import pytest

from scripts.connectors.base_connector import BaseConnector, redact_secrets


class DummyConnector(BaseConnector):
    def _authenticate(self) -> None:
        self._auth_headers = {"Authorization": "Bearer topsecret"}

    def health_check(self) -> bool:
        return True


def test_redaction_scrubs_tokens_from_log_messages(caplog):
    c = DummyConnector()
    with caplog.at_level(logging.INFO):
        c.logger.info("Authorization: Bearer supersecret token=abc123 x-api-key: qwerty")
    assert "supersecret" not in caplog.text
    assert "abc123" not in caplog.text
    assert "qwerty" not in caplog.text


def test_redaction_function_no_secret_leak():
    value = redact_secrets("password=hunter2 secret=mysecret")
    assert "hunter2" not in value
    assert "mysecret" not in value


def test_write_requires_hitl_and_idempotency(monkeypatch):
    monkeypatch.setenv("APOTHEON_CONNECTORS_READ_ONLY", "false")
    c = DummyConnector()
    with pytest.raises(PermissionError):
        c._assert_write_allowed("POST", idempotency_key=None, hitl_approved=True)
    with pytest.raises(PermissionError):
        c._assert_write_allowed("POST", idempotency_key="idem-1", hitl_approved=False)
    c._assert_write_allowed("POST", idempotency_key="idem-1", hitl_approved=True)
