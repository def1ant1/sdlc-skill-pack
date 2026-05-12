# Conversation-to-Structure Extraction Architecture

## Goal
Convert unstructured conversation messages into structured project artifacts (requirements, risks, decisions, tasks, entities), present those as reviewable suggestions, and only persist accepted outcomes.

## Components
1. **Extraction orchestration**
   - Script: `scripts/orchestration/extract_conversation_structure.py`.
   - Responsibilities:
     - Load conversation messages.
     - Generate extraction suggestions per artifact type.
     - Render suggestions for human review before any persistence.
     - Apply review actions (`approve`, `edit`, `reject`, `merge`).
     - Emit final extraction payload suitable for downstream persistence.

2. **Schema layer**
   - Directory: `core/conversation-extraction/schemas/`.
   - Includes schemas for:
     - `requirement`
     - `risk`
     - `decision`
     - `task`
     - `entity`
     - aggregate `extraction-result`

3. **Review lifecycle**
   - Suggestions start in `review_status: suggested`.
   - Review actions transition suggestion state and append entries to `review_log`.
   - `merge` preserves provenance by combining `source_message_ids` and recording merged IDs.

## Input / Output Contracts

### Input messages
Expected as a JSON array. Each message should include:
- `id` (string)
- `text` (string)
- `tags` (array) with values among: `requirements`, `risks`, `decisions`, `tasks`, `entities`

### Review actions
Expected as a JSON array of actions:
- `action`: `approve | edit | reject | merge`
- `suggestion_id`: source suggestion identifier
- `patch` (for `edit`)
- `merge_into` (for `merge`)
- `note` (optional)

### Output
Aggregate result shaped by `extraction-result.schema.json`, including:
- extracted artifact buckets
- source message linkage for each suggestion
- review action history (`review_log`)

## Operational Flow
1. Run extraction script with `--messages` and `--conversation-id`.
2. Inspect the printed review suggestion payload.
3. Optionally provide `--actions` for adjudication.
4. Persist final payload with `--output` after review is complete.

## Example
```bash
python scripts/orchestration/extract_conversation_structure.py \
  --messages /tmp/conversation.json \
  --actions /tmp/review-actions.json \
  --conversation-id convo-123 \
  --output /tmp/extraction.json
```
