# Semantic Cache Policy

## Cache Classes
### Safe
- Public reference summaries
- Deterministic schema snippets
- Non-sensitive skill dependency maps

### Unsafe
- PII/regulated data
- Approval decisions tied to mutable policy state
- Secrets, access tokens, credentials

## Invalidation
Invalidate cache entries when:
1. Source file hash changes
2. Governance policy version changes
3. Skill dependency graph version changes
4. Entry TTL expires

## TTL
- Safe static references: 24h
- Operational routing outputs: 2h
- Sensitive/unsafe classes: no cache allowed

## Lineage Constraints
Each entry must record:
- source_paths
- source_hashes
- policy_version
- created_at
- expires_at
- parent_entry_ids (optional)

Reuse is permitted only when lineage is complete and policy version matches.

## Telemetry Contract Points
- `semantic_cache_lookup`
- `semantic_cache_hit`
- `semantic_cache_miss`
- `semantic_cache_invalidated`
- `semantic_cache_savings_estimated` (fields: tokens_saved_estimate, hit_rate_window)
