# Skill Marketplace and Memory Guide

## Marketplace boundaries
- Treat marketplace skills as governed artifacts requiring policy-aware metadata, validation, and maturity checks.
- Prefer dry-run and contract validation before enabling non-local actions.
- Source onboarding must include a compliant `marketplace-source` definition validated before scheduler activation.
- Ingestion adapters must preserve source timestamps and lineage run identifiers for each normalized listing.

## Ingestion and governance controls
- Use `core/marketplace-ingestion/source_adapters/` for source-specific normalization.
- Use `core/scraping-governor/governance_interceptors/` to enforce legal, robots, ToS, and throttling gates prior to requests.
- Validate source policy files with `scripts/marketplaces/validate_source_policy.py`.
- Follow `references/marketplace-data-policy.md` for boundaries, proxy usage, and violation response.

## Memory model
- Episodic memory captures execution events.
- Semantic memory stores stable promoted facts.
- Organizational/procedural memory tracks reusable patterns and operational runbooks.

See also:
- `core/organizational-memory/README.md`
- `core/procedural-memory/README.md`
- `docs/architecture/memory-engine.md`
