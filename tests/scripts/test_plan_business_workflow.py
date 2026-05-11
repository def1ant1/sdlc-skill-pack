from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
BUSINESS_PLANNER = REPO_ROOT / "scripts" / "orchestration" / "plan_business_workflow.py"


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def test_requires_output_and_flags():
    out = run([sys.executable, str(BUSINESS_PLANNER), "Plan budget"])
    assert out.returncode != 0
    assert "--dry-run" in out.stderr
    assert "--json" in out.stderr
    assert "--output" in out.stderr
