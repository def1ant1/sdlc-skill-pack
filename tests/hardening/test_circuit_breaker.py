from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest import mock
import urllib.error

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.connectors.base_connector import BaseConnector, CircuitOpenBlocked  # noqa: E402


class _TestConnector(BaseConnector):
    def _authenticate(self) -> None:
        self._auth_headers = {"Authorization": "Bearer test"}

    def health_check(self) -> bool:
        return True


def test_invalid_credentials_returns_error_envelope_json():
    c = _TestConnector()
    c._read_only_mode = False

    class _Resp:
        def read(self):
            return b'{"error":"bad token"}'
        def close(self):
            return None

    err = urllib.error.HTTPError("http://x", 401, "Unauthorized", hdrs={}, fp=_Resp())
    with mock.patch("urllib.request.urlopen", side_effect=err):
        try:
            c._request("GET", "http://x")
            assert False
        except RuntimeError as exc:
            payload = json.loads(str(exc))
            assert payload["category"] == "auth"
            assert payload["remediation"]
            assert payload["root_cause_hint"]


def test_circuit_open_blocks_requests():
    c = _TestConnector()
    c._circuit.state = c._circuit.state.OPEN
    c._circuit.opened_at = None
    with mock.patch("scripts.connectors.base_connector._dry_run_enabled", return_value=False):
        try:
            c._request("GET", "http://x")
            assert False
        except CircuitOpenBlocked:
            assert True
