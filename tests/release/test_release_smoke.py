"""Tests for scripts/smoke_test_release.py."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.parent
SMOKE = REPO_ROOT / "scripts" / "smoke_test_release.py"


def run_smoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SMOKE), *args], capture_output=True, text=True)


def test_smoke_passes_in_dry_run_offline_mode():
    result = run_smoke("--dry-run", "--offline")
    assert result.returncode == 0, result.stderr

    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["mode"] == {"dry_run": True, "offline": True}
    assert payload["external_api_calls_required"] is False

    checks = payload["checks"]
    expected = {
        "skill_inventory_load",
        "sdlc_workflow_plan",
        "gtm_workflow_plan",
        "business_workflow_plan",
        "context_packet_build",
        "required_schemas_load",
        "expected_reports_exist",
    }
    assert expected.issubset(checks.keys())
    assert all(check["ok"] for check in checks.values())


def test_smoke_rejects_non_offline_or_non_dry_run_modes():
    result = run_smoke("--dry-run")
    assert result.returncode != 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "fail"
    assert "--dry-run --offline" in payload["error"]
