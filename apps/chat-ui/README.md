# Apotheon Chat UI (MVP)

This Streamlit app provides a browser UI for objective-driven planning with safety-first defaults.

## Features

- Objective submission and domain planner selection.
- Plan/results display from planner JSON output.
- OldFarmTrucks template import from `workflows/examples/oldfarmtrucks-*.json`.
- Schedules visibility via `schedules/registry.yaml`.
- App health, cost, and rate-limit report display from `reports/*.json`.
- Approval gating that blocks live writes by default.

## Safety model

Live writes are blocked by default. The UI only marks the session as approval-ready when:

1. The operator explicitly enables the approval flow checkbox, and
2. The operator provides a non-empty approval ticket/reference.

Even when approval-ready, this MVP only runs planners in `--dry-run` mode.

## Run

```bash
streamlit run apps/chat-ui/streamlit_app.py
```
