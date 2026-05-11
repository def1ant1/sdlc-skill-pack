from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_propose_and_render_and_review(tmp_path: Path) -> None:
    failures = [
        {
            "workflow": "incident-response",
            "skill": "sre-incident-response",
            "failure_reason": "Missing rollback checklist",
            "category": "operations",
        },
        {
            "workflow": "payment-approval",
            "skill": "cash-management",
            "failure_reason": "Approval bypass detected",
            "category": "payments",
        },
    ]
    failures_path = tmp_path / "failures.json"
    failures_path.write_text(json.dumps(failures), encoding="utf-8")

    proposal_path = tmp_path / "runtime" / "evolution" / "proposals.json"
    pr_path = tmp_path / "proposal.md"

    subprocess.run(
        [sys.executable, "scripts/evolution/propose_skill_changes.py", "--failures", str(failures_path), "--output", str(proposal_path)],
        check=True,
    )
    data = json.loads(proposal_path.read_text(encoding="utf-8"))
    assert data["proposal_count"] == 2
    assert all(p["auto_apply_allowed"] is False for p in data["proposals"])
    assert all(p["requires_human_approval"] is True for p in data["proposals"])

    subprocess.run(
        [sys.executable, "scripts/evolution/generate_skill_pr.py", "--proposal", str(proposal_path), "--output", str(pr_path)],
        check=True,
    )
    pr_text = pr_path.read_text(encoding="utf-8")
    assert "Auto-apply: **Disabled**" in pr_text

    blocked = subprocess.run(
        [sys.executable, "scripts/evolution/review_skill_change.py", "--proposal", str(proposal_path)],
        check=False,
    )
    assert blocked.returncode == 2

    approved = subprocess.run(
        [sys.executable, "scripts/evolution/review_skill_change.py", "--proposal", str(proposal_path), "--approved-by", "human@example.com"],
        check=False,
    )
    assert approved.returncode == 0
