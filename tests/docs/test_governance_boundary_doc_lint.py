from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DOMAIN_REFERENCES = {
    "finance": "docs/governance/financial-controls.md",
    "legal": "docs/governance/professional-advice-boundaries.md",
    "hr": "docs/governance/hr-high-impact-decision-policy.md",
    "procurement": "docs/governance/external-action-policy.md",
    "customer outreach": "docs/governance/external-action-policy.md",
    "scraping": "docs/governance/data-scraping-policy.md",
}

DOMAIN_SKILL_FILES = {
    "finance": ["skills/finance-accounting-phase-pack/SKILL.md"],
    "legal": ["skills/legal-operations-phase-pack/SKILL.md"],
    "hr": ["skills/hr-operations-phase-pack/SKILL.md"],
    "procurement": ["skills/vendor-procurement-phase-pack/SKILL.md"],
    "customer outreach": ["skills/sales-marketing-customer-phase-pack/SKILL.md"],
    "scraping": [
        "skills/competitor-price-scraping/SKILL.md",
        "skills/local-market-data-collection/SKILL.md",
    ],
}


def test_required_governance_boundary_docs_exist() -> None:
    for policy_path in REQUIRED_DOMAIN_REFERENCES.values():
        assert (REPO_ROOT / policy_path).exists(), f"Missing policy doc: {policy_path}"


def test_applicable_domains_reference_required_boundary_docs() -> None:
    for domain, policy_path in REQUIRED_DOMAIN_REFERENCES.items():
        for skill_rel_path in DOMAIN_SKILL_FILES[domain]:
            content = (REPO_ROOT / skill_rel_path).read_text()
            assert policy_path in content, (
                f"{skill_rel_path} must reference {policy_path} for domain '{domain}'"
            )
