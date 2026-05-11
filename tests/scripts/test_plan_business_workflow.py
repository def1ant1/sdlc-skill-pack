from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
GTM_PLANNER = REPO_ROOT / "scripts" / "orchestration" / "plan_gtm_workflow.py"
BUSINESS_PLANNER = REPO_ROOT / "scripts" / "orchestration" / "plan_business_workflow.py"

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def test_ambiguous_objective_sets_diagnostic_flag():
    out = run([sys.executable, str(GTM_PLANNER), "Improve content and SEO performance"])
    assert out.returncode == 0
    data = json.loads(out.stdout)
    assert data["planner_diagnostics"]["ambiguous_routing"] is True

def test_missing_skill_remediation_message_is_clear():
    out = run([sys.executable, str(BUSINESS_PLANNER), "Finance budget planning"])
    assert out.returncode == 1
    err = out.stderr.strip().lower()
    assert "required skills unavailable" in err
    assert "install or add missing skills" in err
