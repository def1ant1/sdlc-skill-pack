# License Review Checklist

Use this checklist before shipping releases, publishing packages, or announcing feature tiers.

## 1) OSS distribution checks

- Confirm repository license file is present and current.
- Confirm new source files include required headers (if policy requires).
- Confirm bundled assets, templates, and examples are distributable.
- Confirm generated artifacts do not include restricted third-party content.

## 2) Dependency license checks

- Inventory direct and transitive dependencies for runtime/tooling/docs.
- Record each dependency license and policy compatibility.
- Flag copyleft or source-disclosure-triggering licenses for legal review.
- Track attribution/notice requirements for distribution.

## 3) Feature-tier boundary checks

- Ensure OSS docs do not imply hosted/cloud/enterprise availability.
- Ensure enterprise-only items are labeled as future/commercial where applicable.
- Ensure roadmap references do not conflict with current OSS claims.
- Ensure onboarding docs reflect local-first behavior and current feature availability.

## 4) Trademark and branding checks

- Verify third-party names/logos are used under applicable terms.
- Verify product naming is consistent across docs and release artifacts.

## 5) Release decision record

For each release:

- Date:
- Reviewer:
- Scope reviewed (code/docs/dependencies):
- Boundary risks identified:
- Actions required before release:
- Final decision (approve/block):

## References

- Commercial overview: `COMMERCIAL.md`
- Boundary details: `docs/commercial/open-core-boundary.md`
- Changelog: `CHANGELOG.md`
