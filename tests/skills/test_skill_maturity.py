import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
GRADE = REPO_ROOT / "scripts" / "grade_skill_maturity.py"
CERTIFY = REPO_ROOT / "scripts" / "certify_skill.py"


def test_grade_skill_maturity_writes_report_and_enforces_thresholds(tmp_path: Path):
    for name in [
        "cash-flow-forecasting",
        "financial-management",
        "revenue-leakage-detection",
        "process-optimization-phase-pack",
        "finance-accounting-phase-pack",
    ]:
        d = tmp_path / "skills" / name
        (d / "examples").mkdir(parents=True)
        (d / "manifest.v9.json").write_text('{"governance_level":"high","human_approval_required":true,"telemetry_events":[1],"eval_metrics":[1],"failure_modes":[1],"input_contract":{},"output_contract":{},"data_contracts":[1]}')
        (d / "SKILL.md").write_text("""---
name: demo
description: demo
use_when: x
do_not_use_when: y
metadata:
  manifest: manifest.v9.json
---
input_contract
output_contract
entity
event
governance
human approval
telemetry
failure
boundary
""")

    run = subprocess.run([sys.executable, str(GRADE), "--root", str(tmp_path)], capture_output=True, text=True)
    assert run.returncode == 0
    report = (tmp_path / "reports" / "skill_maturity_report.md").read_text(encoding="utf-8")
    assert "MVP L3+" in report
    assert "High-risk critical MVP at L5" in report


def test_certify_skill_rejects_without_required_checks(tmp_path: Path):
    d = tmp_path / "skills" / "demo-skill"
    d.mkdir(parents=True)
    (d / "manifest.v9.json").write_text("{}", encoding="utf-8")

    report = tmp_path / "reports" / "skill_certification_report.md"
    run = subprocess.run([sys.executable, str(CERTIFY), str(d), "--report", str(report)], capture_output=True, text=True)
    assert run.returncode == 1
    assert '"status": "rejected"' in run.stdout
    assert report.exists()
