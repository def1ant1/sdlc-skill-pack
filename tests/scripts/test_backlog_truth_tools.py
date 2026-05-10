from pathlib import Path
import subprocess, sys

REPO_ROOT = Path(__file__).parent.parent.parent
EXTRACT = REPO_ROOT / 'scripts' / 'extract_backlog_paths.py'
VALIDATE = REPO_ROOT / 'scripts' / 'validate_backlog_truth.py'

def test_extract_emits_phase_and_path():
    out = subprocess.run([sys.executable, str(EXTRACT), '--root', str(REPO_ROOT)], capture_output=True, text=True)
    assert out.returncode == 0
    assert '"path"' in out.stdout

def test_ignore_suppresses_missing(tmp_path: Path):
    (tmp_path/'TEST_BACKLOG.md').write_text('## Phase 1\nmissing/path.md\n')
    (tmp_path/'scripts').mkdir()
    (tmp_path/'scripts'/'extract_backlog_paths.py').write_text(EXTRACT.read_text())
    (tmp_path/'scripts'/'validate_backlog_truth.py').write_text(VALIDATE.read_text())
    (tmp_path/'.backlog-truth-ignore.yaml').write_text('ignore_paths:\n  - missing/path.md\n')
    out = subprocess.run([sys.executable, str(tmp_path/'scripts'/'validate_backlog_truth.py'), '--root', str(tmp_path)], capture_output=True, text=True)
    assert out.returncode == 0
