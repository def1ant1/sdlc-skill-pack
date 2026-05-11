from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS = [
    "trading-research",
    "market-data-ingestion",
    "watchlist-management",
    "portfolio-risk-analysis",
    "technical-analysis-support",
    "fundamental-analysis-support",
    "crypto-market-analysis",
    "fx-market-analysis",
    "correlation-regime-analysis",
    "position-sizing-analysis",
    "trade-journal-analysis",
    "backtesting-support",
    "risk-limit-monitoring",
    "cross-market-price-comparison",
    "fee-slippage-modeling",
    "liquidity-risk-analysis",
    "execution-risk-analysis",
    "crypto-arbitrage-monitoring",
    "fx-arbitrage-analysis",
    "retail-arbitrage-analysis",
]

FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "trading-research"


def _skill_text(skill: str) -> str:
    return (REPO_ROOT / "skills" / skill / "SKILL.md").read_text().lower()


def test_trading_research_skill_directories_and_docs_exist():
    for skill in SKILLS:
        path = REPO_ROOT / "skills" / skill
        assert path.is_dir(), f"Missing skill directory: {skill}"
        assert (path / "SKILL.md").is_file(), f"Missing SKILL.md for: {skill}"


def test_all_skills_default_to_offline_dry_run_with_local_csv_and_fixtures():
    assert FIXTURE_DIR.is_dir()
    required_fixtures = {
        "README.md",
        "market_prices_sample.csv",
        "portfolio_positions_sample.csv",
        "execution_costs_sample.csv",
        "trade_journal_sample.csv",
    }
    for fixture in required_fixtures:
        assert (FIXTURE_DIR / fixture).is_file(), f"Missing fixture: {fixture}"

    for skill in SKILLS:
        text = _skill_text(skill)
        assert "offline/dry-run" in text
        assert "local csv" in text
        assert "tests/fixtures/trading-research" in text


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


def test_order_placement_disabled_hitl_required_and_no_autonomous_trading():
    for skill in SKILLS:
        text = _skill_text(skill)
        assert "order placement is disabled by default" in text
        assert "human-in-the-loop (hitl) approval" in text
        assert "autonomous trading is prohibited" in text


def test_no_personalized_advice_no_guaranteed_returns_and_no_prohibited_or_evasive_conduct_support():
    prohibited_assistance = ["manipulation", "insider trading", "spoofing", "evasive guidance", "circumvention"]
    for skill in SKILLS:
        text = _skill_text(skill)
        assert "do not provide personalized final investment advice" in text
        assert "do not claim guaranteed returns" in text
        assert "do not provide support for prohibited market conduct" in text
        for term in prohibited_assistance:
            assert term in text


def test_backtesting_and_governance_validation_coverage_present():
    backtesting_text = _skill_text("backtesting-support")
    assert "offline/dry-run" in backtesting_text
    assert "research hypotheses" in backtesting_text

    governance_policy = (
        REPO_ROOT / "docs" / "governance" / "trading-research-governance.md"
    ).read_text().lower()
    for phrase in [
        "research-only",
        "no autonomous trading",
        "no market manipulation",
        "offline/dry-run",
        "human-in-the-loop",
    ]:
        assert phrase in governance_policy
