# Rate Limit and Quota Standard

## Policy contract
All connectors MUST declare:
- `connector_id`
- `requests_per_minute`
- `daily_quota` (or explicit `null` if provider does not enforce)
- Degradation thresholds:
  - `degrade_to_cached_at`
  - `degrade_to_read_only_at`

## Degradation strategy
When quota pressure increases:
1. **Normal**: live connector calls allowed.
2. **Elevated** (remaining budget <= `degrade_to_cached_at`): prefer cached/stale reads.
3. **Critical** (remaining budget <= `degrade_to_read_only_at`): enforce read-only mode and skip non-essential writes.

## Scheduler behavior
Schedulers MUST check quota pressure before selecting connector-backed actions.
If pressure is `critical`, workflows should pivot to cached artifacts or defer write-heavy tasks.
