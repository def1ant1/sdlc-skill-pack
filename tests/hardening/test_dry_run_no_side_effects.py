from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "runtime"))

from scripts.connectors.base_connector import BaseConnector, DryRunSideEffectBlocked  # noqa: E402
from execute_workflow import execute_local  # noqa: E402


class _TestConnector(BaseConnector):
    def _authenticate(self) -> None:
        self._auth_headers = {"Authorization": "Bearer test"}

    def health_check(self) -> bool:
        return True


def test_connector_dry_run_blocks_network_write_without_urlopen():
    c = _TestConnector()
    with mock.patch.dict(os.environ, {"APOTHEON_DRY_RUN": "true"}), \
         mock.patch("urllib.request.urlopen") as mocked:
        try:
            c._request("POST", "http://example.com", payload={"x": 1}, idempotency_key="k", hitl_approved=True)
            assert False
        except DryRunSideEffectBlocked:
            pass
    mocked.assert_not_called()


def test_execute_local_dry_run_never_invokes_skill_activity():
    plan = {"plan_id": "p", "objective": "o", "skill_chain": [{"step": 1, "skill": "backend-engineering"}]}
    with mock.patch("execute_workflow.run_skill_activity") as run_skill:
        log = execute_local(plan, dry_run=True)
    run_skill.assert_not_called()
    assert log["status"] == "dry_run"
