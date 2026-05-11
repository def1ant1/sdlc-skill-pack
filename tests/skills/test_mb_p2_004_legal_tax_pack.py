from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _manifest() -> dict:
    return json.loads((REPO_ROOT / "skills" / "legal-operations-phase-pack" / "manifest.v9.json").read_text())


def test_mb_p2_004_decision_support_only_boundaries_present() -> None:
    manifest = _manifest()
    boundaries = manifest["decision_support_boundaries"]
    assert boundaries["support_only"] is True
    assert boundaries["prohibit_final_legal_or_tax_advice"] is True
    assert boundaries["mandatory_non_advisory_notice"] is True


def test_mb_p2_004_authoritative_citation_and_structured_finding_fields() -> None:
    manifest = _manifest()

    citations = manifest["authoritative_citation_policy"]
    assert citations["required"] is True
    assert "primary-law" in citations["source_priority"]
    assert "regulatory-agency" in citations["source_priority"]

    required_fields = set(manifest["finding_schema_requirements"]["required_fields"])
    assert {
        "jurisdiction",
        "authority_level",
        "effective_date",
        "retrieved_at",
        "verified_at",
        "confidence",
        "professional_review_required",
    }.issubset(required_fields)


def test_mb_p2_004_filing_and_regulatory_actions_are_approval_gated() -> None:
    controls = _manifest()["approval_controls"]
    assert controls["required_for_filings_and_submissions"] is True
    assert controls["required_for_regulatory_actions"] is True
    assert controls["required_for_tax_or_legal_entity_mutations"] is True
