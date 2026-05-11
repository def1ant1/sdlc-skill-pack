# Getting Started

Phase 0 starter documentation. Expand this document as the platform matures.

## CLI quickstart

Copy/paste examples:

```bash
# List workflow execution history (human-readable)
apotheon workflows list

# List workflow execution history as JSON
apotheon workflows list --json

# Plan a workflow (dry-run by default)
apotheon workflows run "Harden CI pipeline security posture"

# Plan and execute workflow (opt-in)
apotheon workflows run --execute "Harden CI pipeline security posture"

# Preview schedule windows
apotheon schedules preview --count 3

# Execute due schedules for the lookback window
apotheon schedules run-due --lookback-minutes 120

# List schedule run artifacts
apotheon runs list

# List schedule run artifacts as JSON
apotheon runs list --output json
```
