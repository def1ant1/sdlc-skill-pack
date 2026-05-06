from pathlib import Path


def test_required_root_docs_exist():
    for name in ['README.md', 'ROADMAP.md', 'CONTRIBUTING.md', 'CHANGELOG.md']:
        assert Path(name).exists()


def test_shared_baselines_exist():
    assert Path('shared/standards/security-baseline.md').exists()
    assert Path('shared/policies/ai-safety-policy.md').exists()
