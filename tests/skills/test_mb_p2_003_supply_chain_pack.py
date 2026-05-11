from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_inventory_product_market_pack_has_scraping_and_approval_controls() -> None:
    manifest = json.loads((REPO_ROOT / "skills" / "inventory-product-market-phase-pack" / "manifest.v9.json").read_text())

    controls = manifest["approval_controls"]
    assert controls["required_for_purchase_actions"] is True
    assert controls["required_for_listing_actions"] is True
    assert controls["required_for_vendor_outreach"] is True

    scraping = manifest["scraping_policy_controls"]
    assert scraping["require_robots_check"] is True
    assert scraping["require_terms_of_use_check"] is True
    assert scraping["require_rate_limit_enforcement"] is True
    assert scraping["require_operator_approval_for_restricted_sources"] is True


def test_oldfarmtrucks_market_scan_fixture_supports_dry_run_acquisition_pricing() -> None:
    fixture = json.loads((REPO_ROOT / "workflows" / "examples" / "oldfarmtrucks-market-scarcity-scan.json").read_text())

    assert fixture["dry_run_validation"]["required"] is True
    assert "acquisition-screening" in fixture["dry_run_validation"]["scenarios"]
    assert "pricing-adjustment-simulation" in fixture["dry_run_validation"]["scenarios"]

    skills = [step["skill"] for step in fixture["plan"]["skill_chain"]]
    for required in [
        "demand-planning",
        "sku-margin-analysis",
        "stockout-risk-detection",
        "supplier-risk-intelligence",
        "purchase-approval-routing",
        "scarcity-analysis",
        "arbitrage-analysis",
    ]:
        assert required in skills
