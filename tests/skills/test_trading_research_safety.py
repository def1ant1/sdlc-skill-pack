from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS = [
    "market-ingestion-research",
    "watchlist-research",
    "risk-research",
    "technical-fundamental-analysis-research",
    "crypto-fx-research",
    "position-sizing-research",
    "trading-journal-research",
    "backtesting-research",
    "risk-limits-research",
    "news-synthesis-research",
]


def _skill_text(skill: str) -> str:
    return (REPO_ROOT / "skills" / skill / "SKILL.md").read_text().lower()


def test_trading_research_skill_directories_and_docs_exist():
    for skill in SKILLS:
        path = REPO_ROOT / "skills" / skill
        assert path.is_dir(), f"Missing skill directory: {skill}"
        assert (path / "SKILL.md").is_file(), f"Missing SKILL.md for: {skill}"


def test_all_skills_default_to_offline_dry_run_with_local_csv():
    for skill in SKILLS:
        text = _skill_text(skill)
        assert "offline/dry-run" in text
        assert "local csv" in text


def test_all_skills_require_hypothesis_risk_assumptions_horizon_invalidation():
    required = [
        "research hypotheses",
        "risk factors",
        "assumptions",
        "time horizon",
        "invalidation criteria",
    ]
    for skill in SKILLS:
        text = _skill_text(skill)
        for phrase in required:
            assert phrase in text, f"{skill} missing phrase: {phrase}"


def test_order_placement_disabled_and_hitl_required():
    for skill in SKILLS:
        text = _skill_text(skill)
        assert "order placement is disabled by default" in text
        assert "human-in-the-loop (hitl) approval" in text


def test_no_personalized_advice_no_guaranteed_returns_no_prohibited_conduct_support():
    prohibited_assistance = ["manipulation", "insider trading", "spoofing"]
    for skill in SKILLS:
        text = _skill_text(skill)
        assert "do not provide personalized final investment advice" in text
        assert "do not claim guaranteed returns" in text
        assert "do not provide support for prohibited market conduct" in text
        for term in prohibited_assistance:
            assert term in text
