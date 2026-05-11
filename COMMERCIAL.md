# Commercial Model Overview

This repository is open-source and designed to run locally-first. The current codebase focuses on self-hosted workflows, local orchestration, and human-reviewed automation.

## What is open-source and available now (local OSS)

The following capabilities are included in the open-source project and intended for local/self-managed operation:

- Local workflow planning/execution with dry-run-first defaults.
- Local connector patterns and health checks.
- Governance artifacts, policy docs, and approval-gate schemas.
- Documentation, runbooks, and onboarding for local and Docker-based operation.
- Skill authoring/validation, registry scaffolding, and pre-merge quality checks.

## Future commercial tiers (not currently provided by this repo)

The project roadmap may include hosted/cloud/enterprise offerings in the future. Examples of potential commercial capabilities include:

- Managed hosted control plane and uptime-backed operations.
- Enterprise SSO/SAML, advanced RBAC, and organization-wide audit tooling.
- Multi-tenant administration and centralized policy management UI.
- Managed connector lifecycle, premium integrations, and support SLAs.
- Enterprise compliance packages, dedicated support, and deployment services.

These capabilities are **not included** in the current OSS codebase unless explicitly released with corresponding documentation.

## Boundary principles

1. **No implied entitlement**: Future hosted/cloud/enterprise features are not granted by OSS access alone.
2. **Roadmap is not contract**: Planned items are directional and may change.
3. **License controls usage**: Rights are governed by the repository license and third-party dependency licenses.
4. **Clear packaging**: OSS artifacts and any future commercial services are versioned and communicated separately.

## Practical guidance

- If a capability is documented in this repository and shipped in code, treat it as OSS-available (subject to license).
- If a capability is described as hosted/cloud/enterprise and not implemented here, treat it as future/commercial and unavailable in local OSS by default.
- For ambiguous cases, use `LICENSE_REVIEW.md` and `docs/commercial/open-core-boundary.md` as the source of truth.

## Related documents

- Licensing checklist: `LICENSE_REVIEW.md`
- Open-core boundary definition: `docs/commercial/open-core-boundary.md`
- Main project documentation index: `README.md`
