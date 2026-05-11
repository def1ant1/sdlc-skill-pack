# Profile Selection Reference

This reference defines product profiles, capability boundaries, and Compose profile mapping.

## Product profiles

| Profile | Primary use | MVP-only | High-risk default | Compose profiles |
| --- | --- | --- | --- | --- |
| `local-solo` | Single operator on consumer hardware | Yes | Disabled | `local-solo,core` |
| `mvp` | Release-critical validation | Yes | Disabled | `mvp,core,observability` |
| `team` | Small-team shared environment | No | Guarded | `team,core,observability,collaboration` |
| `enterprise` | Governance-heavy production baseline | No | Guarded | `enterprise,core,observability,governance,integrations` |
| `full-domain-lab` | Broad cross-domain experimentation | No | Guarded | `full-domain-lab,core,observability,governance,integrations,experiments` |

## Capability boundaries

- `local-solo` and `mvp` are **MVP-only** profiles and include only release-critical workflows.
- High-risk categories (financial transfers, policy mutations, legal/HR high-impact actions, destructive data actions, and infrastructure mutations) are **disabled by default** in every profile.
- `team`, `enterprise`, and `full-domain-lab` may allow high-risk workflows only through explicit HITL-enabled policy paths.

## Usage

```bash
# Validate all profile YAML files against schema and fallback checks
python scripts/validation/validate_profiles.py

# Start Compose with profile-mapped services (example)
COMPOSE_PROFILES=mvp,core,observability docker compose up -d
```

## Constraints

- Do not enable high-risk capabilities without governance controls.
- Keep MVP profile scope limited to release-critical skills/workflows.
- Ensure product profile `compose_profiles` values remain aligned with deployment profile conventions.
