from pathlib import Path
import json
import subprocess
import sys

REPO_ROOT = Path(__file__).parent.parent.parent
EXTRACT = REPO_ROOT / "scripts" / "extract_backlog_paths.py"
VALIDATE = REPO_ROOT / "scripts" / "validate_backlog_truth.py"
REPORT = REPO_ROOT / "scripts" / "generate_repo_truth_report.py"


def test_extract_emits_phase_and_path(tmp_path: Path):
    backlog = tmp_path / "X_BACKLOG.md"
    backlog.write_text("## Phase 3\n- build scripts/alpha.py\n")
    out = subprocess.run([sys.executable, str(EXTRACT), "--root", str(tmp_path)], capture_output=True, text=True)
    assert out.returncode == 0
    data = json.loads(out.stdout)
    assert data[0]["phase"] == "Phase 3"
    assert data[0]["path"] == "scripts/alpha.py"


def test_ignore_suppresses_missing(tmp_path: Path):
    (tmp_path / "TEST_BACKLOG.md").write_text("## Phase 1\nmissing/path.md\n")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "extract_backlog_paths.py").write_text(EXTRACT.read_text())
    (tmp_path / "scripts" / "validate_backlog_truth.py").write_text(VALIDATE.read_text())
    (tmp_path / ".backlog-truth-ignore.yaml").write_text("ignore_paths:\n  - missing/path.md\n")
    out = subprocess.run(
        [sys.executable, str(tmp_path / "scripts" / "validate_backlog_truth.py"), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0


def test_truth_report_generation(tmp_path: Path):
    (tmp_path / "TEST_BACKLOG.md").write_text("## Phase 1\n- scripts/present.py\n")
    (tmp_path / "scripts").mkdir()
    for s in ["extract_backlog_paths.py", "validate_backlog_truth.py", "generate_repo_truth_report.py"]:
        (tmp_path / "scripts" / s).write_text((REPO_ROOT / "scripts" / s).read_text())
    (tmp_path / "scripts" / "present.py").write_text("print('ok')\n")
    out = subprocess.run([sys.executable, str(tmp_path / "scripts" / "generate_repo_truth_report.py"), "--root", str(tmp_path)], capture_output=True, text=True)
    assert out.returncode == 0
    assert (tmp_path / "reports" / "repo_truth_report.md").exists()
    assert (tmp_path / "reports" / "repo_truth_report.json").exists()
