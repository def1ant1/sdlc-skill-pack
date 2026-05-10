---
name: multimodal-runtime
description: Processes multi-modal enterprise inputs (PDF, image, audio, video) through a unified pipeline with modality routing and context assembly for the Enterprise OS.
metadata:
  version: "0.1.0"
  category: cognitive
  owner: platform
  maturity: draft
  dependencies: ['cognitive-runtime', 'data-fabric', 'agent-kernel']

use_when:
  - Follow description activation criteria.
do_not_use_when:
  - Request is clearly outside this skill domain.
context_loading:
  default_level: L2
  levels:
    L1:
      max_tokens: 2000
    L2:
      max_tokens: 8000
    L3:
      max_tokens: 16000
telemetry_contract:
  estimated_token_savings_event: semantic_cache_savings_estimated
  cache_hit_rate_event: semantic_cache_hit
---

## Role

Unified input processing pipeline for multi-modal enterprise content. Accepts documents,
images, audio recordings, and video as first-class inputs alongside text. Routes each
modality to the appropriate processing skill, assembles extracted content into a unified
context object, and delivers structured, searchable enterprise intelligence to downstream
agents and skills.

## Activation Triggers

- An enterprise document (PDF, Word, Excel) is submitted for processing
- A meeting recording or audio file is ingested for transcription and analysis
- An image or screenshot is submitted for visual interpretation
- A video is submitted for frame analysis or content extraction
- A workflow step requires multi-modal context assembly from heterogeneous inputs
- `data-fabric` ingests a new multi-modal asset that requires indexing

## Execution Protocol

1. **Modality detection**: Identify input modality from MIME type and file extension:
   - `document`: PDF, DOCX, XLSX, PPTX → route to `document-intelligence`
   - `image`: PNG, JPG, TIFF, screenshot → route to `visual-analytics`
   - `audio`: MP3, WAV, M4A, OGG → route to `audio-video-processing`
   - `video`: MP4, MOV, AVI → route to `audio-video-processing` (with frame extraction)
   - `text`: plain text, markdown, HTML → pass directly to text pipeline

2. **Parallel processing**: For multi-modal submissions (e.g., a video with embedded slides),
   process modalities in parallel. Each modality processor returns a structured extract.

3. **Context assembly**: Merge extracts from all modalities into a unified context object:
   - Normalized text content (OCR text, transcriptions, extracted tables)
   - Structured data (parsed tables, named entities, key-value pairs)
   - Visual annotations (chart descriptions, diagram interpretations)
   - Metadata (document author, recording timestamp, page counts)

4. **Indexing**: Submit the assembled context to `enterprise-search` for indexing.
   Tag with source modalities, content classification, and data governance labels.

5. **Return**: Return the unified context object to the requesting skill or agent.

## Output Format

```yaml
multimodal_result:
  input_id: "MM-2026-xxxxx"
  modalities_processed: [document, audio]
  status: success | partial | failed
  context:
    text_content: "..."         # Combined text from all modalities
    structured_data: []         # Tables, key-value pairs
    visual_annotations: []      # Chart/diagram descriptions
    entities: []                # Named entities across all modalities
    metadata:
      page_count: 0
      duration_seconds: 0
      languages_detected: [en]
  processing_time_ms: 0
  index_ref: "enterprise-search/doc/MM-2026-xxxxx"
```

## References

- `references/` — Modality routing table, context assembly schema, supported format matrix
