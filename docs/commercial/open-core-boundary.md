# Open-Core Boundary: OSS vs Hosted/Cloud/Enterprise

This document defines the product boundary between what is currently available in open-source local operation and what may be offered in future commercial tiers.

## Scope and intent

- Prevent confusion about what users can run locally today.
- Keep roadmap/aspirational statements separate from shipped OSS functionality.
- Provide a single boundary reference for README, onboarding, and release notes.

## OSS local capabilities (current)

The OSS repository currently supports local/self-managed operation patterns such as:

- Local or Docker-based setup and execution.
- Dry-run-first workflow planning and runbook-driven operations.
- Policy/gate scaffolding and governance documentation.
- Connector framework + local app connectivity patterns.
- Local reports, diagnostics, and validation scripts.

Availability standard: if it is shipped in this repository and documented in operational docs, it is OSS-local.

## Future hosted/cloud/enterprise capabilities (potential)

These are examples of capabilities that may exist outside the OSS local boundary in future offerings:

- Hosted control plane with managed reliability and operations.
- Enterprise identity/access (SSO/SAML/SCIM), org-level administration.
- Centralized multi-workspace governance and policy management.
- Premium integrations, managed scaling, and contractual SLAs.
- Dedicated support, onboarding services, and compliance programs.

Unless explicitly added to this repo and documented as OSS, treat these as non-OSS and unavailable locally.

## Naming and documentation rules

1. Use **"OSS local"** for shipped repository functionality.
2. Use **"future hosted/cloud/enterprise"** for non-shipped, non-OSS capabilities.
3. Do not present roadmap items as currently available features.
4. Cross-link boundary docs from README and onboarding entrypoints.

## Decision matrix

- **In code + in docs + runnable locally** → OSS local capability.
- **Only in roadmap/changelog aspirations** → not guaranteed; not current OSS capability.
- **Only in commercial packaging statements** → future/commercial boundary.

## Conflict resolution

If documentation conflicts:

1. `docs/commercial/open-core-boundary.md` (this document)
2. `COMMERCIAL.md`
3. Onboarding pages
4. README summaries

## Related references

- `COMMERCIAL.md`
- `LICENSE_REVIEW.md`
- `README.md`
- `docs/onboarding/getting-started.md`
