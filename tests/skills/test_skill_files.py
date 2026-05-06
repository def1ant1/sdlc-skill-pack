from pathlib import Path


def test_system_architecture_skill_exists():
    assert Path('skills/system-architecture/SKILL.md').exists()


def test_core_skills_exist():
    assert Path('core/orchestration/SKILL.md').exists()
    assert Path('core/memory-token-management/SKILL.md').exists()
