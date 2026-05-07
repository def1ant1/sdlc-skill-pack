# Versioning Guide

## Semantic Versioning (SemVer)

All services, packages, and APIs use Semantic Versioning: `MAJOR.MINOR.PATCH[-prerelease]`

```
1.4.2
│ │ └── PATCH: backwards-compatible bug fix
│ └──── MINOR: new backwards-compatible functionality
└────── MAJOR: breaking change (incompatible API change)
```

Version `0.x.x` indicates pre-stable (breaking changes may occur in MINOR).
Version `1.0.0` is the stability commitment: MAJOR increments for breaks.

---

## When to Increment What

### MAJOR (x.0.0)

Increment when any of the following are true:

| Scenario | Example |
|---|---|
| API endpoint removed | `DELETE /v1/accounts/{id}` removed |
| API response field removed | `account.type` field dropped |
| API field type changed | `account.id` changed from `int` to `string` |
| Breaking authentication change | Token format changed |
| Event schema breaking change | `account.created` payload restructured |
| Required config/env var removed | `DATABASE_URL` renamed |

### MINOR (0.x.0)

Increment when:

| Scenario | Example |
|---|---|
| New API endpoint added | `GET /v1/accounts/{id}/usage` added |
| New optional response field | `account.metadata` field added |
| New optional request parameter | `?include=usage` query param added |
| New event type | `account.upgraded` event added |
| New optional config | `LOG_LEVEL` env var added with default |
| Significant new feature | Dashboard export functionality |

### PATCH (0.0.x)

Increment when:

| Scenario | Example |
|---|---|
| Bug fix with no API change | Incorrect calculation corrected |
| Performance improvement | Query optimization |
| Dependency security update | Upgraded vulnerable library |
| Documentation update only | README clarification |

---

## Pre-release Identifiers

| Identifier | Meaning | Example |
|---|---|---|
| `alpha` | Unstable; breaking changes expected | `2.0.0-alpha.1` |
| `beta` | Feature-complete; bugs possible | `2.0.0-beta.3` |
| `rc` | Release candidate; production-ready barring regressions | `2.0.0-rc.1` |

Pre-releases must NOT be deployed to production without explicit operator approval.

---

## API Versioning Strategy

URL versioning is the primary mechanism (`/v1/`, `/v2/`):

- Old major version stays alive for minimum 6 months after new version GA
- `Deprecation: Sat, 01 Jan 2027 00:00:00 GMT` header sent in all deprecated version responses
- `Sunset: Sat, 01 Jul 2027 00:00:00 GMT` header when removal date is confirmed
- Customer communication required 90 days before any version sunset

---

## Changelog Format (Keep a Changelog)

```markdown
# Changelog

## [Unreleased]

## [1.4.2] - 2026-05-06
### Fixed
- Invoice totals now correctly include tax for EU accounts (#1234)

## [1.4.1] - 2026-04-20
### Fixed
- Pagination cursor now correctly handles empty result sets (#1198)

## [1.4.0] - 2026-04-01
### Added
- Account usage endpoint: `GET /v1/accounts/{id}/usage`
- `include=usage` parameter on account detail endpoint

### Changed
- Invoice line items now sorted by date descending by default

## [1.3.0] - 2026-03-01
...
```

Sections: `Added` | `Changed` | `Deprecated` | `Removed` | `Fixed` | `Security`

Breaking changes must be called out in a `### ⚠ Breaking Changes` subsection at the top.

---

## Git Tagging

Tags are the authoritative version source:

```bash
git tag -a v1.4.2 -m "Release v1.4.2: Fix invoice tax calculation for EU accounts"
git push origin v1.4.2
```

- Tags are immutable; never move or delete a published tag
- Pre-release tags: `v2.0.0-beta.1`
- Tags trigger the release CI pipeline automatically