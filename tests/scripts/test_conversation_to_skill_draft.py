import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "skills" / "conversation_to_skill_draft.py"


def test_draft_review_mode_outputs_artifact_without_writing():
    proc = subprocess.run(
        ["python", str(SCRIPT), "--name", "demo-skill", "--conversation", "Purpose: automate intake. Must not write without approval. Require review approval."],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert proc.returncode == 0
    assert "GENERATED SKILL ARTIFACT" in proc.stdout
    assert "Write skipped" in proc.stdout
    assert not (REPO_ROOT / "skills" / "demo-skill").exists()
