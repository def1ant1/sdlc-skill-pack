# Multi-Modal Runtime — Modality Routing Table & Context Assembly Schema

## Modality Detection & Routing

| MIME Type | Extension(s) | Modality | Processing Skill | Priority |
|-----------|-------------|----------|-----------------|---------|
| application/pdf | .pdf | document | document-intelligence | high |
| application/vnd.openxmlformats-officedocument.wordprocessingml.document | .docx | document | document-intelligence | high |
| application/vnd.ms-excel | .xlsx, .xls | document | document-intelligence | high |
| application/vnd.ms-powerpoint | .pptx, .ppt | document | document-intelligence | high |
| image/png | .png | image | visual-analytics | medium |
| image/jpeg | .jpg, .jpeg | image | visual-analytics | medium |
| image/tiff | .tiff, .tif | image | visual-analytics | medium |
| audio/mpeg | .mp3 | audio | audio-video-processing | medium |
| audio/wav | .wav | audio | audio-video-processing | medium |
| audio/mp4 | .m4a | audio | audio-video-processing | medium |
| video/mp4 | .mp4 | video | audio-video-processing | low |
| video/quicktime | .mov | video | audio-video-processing | low |
| text/plain | .txt | text | direct (no skill needed) | high |
| text/markdown | .md | text | direct (no skill needed) | high |

---

## Multi-Modal Submission Schema

```yaml
multimodal_request:
  request_id: "MM-REQ-2026-xxxxx"
  submitted_by: "program-governance-agent"
  submitted_at: "2026-05-07T10:00:00Z"

  inputs:
    - input_id: "input-001"
      modality: document
      source: "s3://enterprise-os-docs/Q2-board-deck.pdf"
      mime_type: "application/pdf"
      size_bytes: 4200000

    - input_id: "input-002"
      modality: audio
      source: "s3://enterprise-os-recordings/board-meeting-2026-05-07.mp4"
      mime_type: "audio/mp4"
      size_bytes: 156000000

  processing_options:
    extract_tables: true
    extract_entities: true
    transcribe_audio: true
    diarize_speakers: true
    extract_action_items: true
    language_hint: en
    ocr_if_scanned: true

  output_format: unified_context    # unified_context | per_modality | structured_json
```

---

## Unified Context Assembly Schema

```yaml
unified_context:
  context_id: "MM-CTX-2026-xxxxx"
  assembled_at: "2026-05-07T10:05:00Z"
  input_count: 2
  modalities: [document, audio]

  # Combined text content from all modalities
  text_content: |
    [Document: Q2 Board Deck]
    ## Q2 Financial Performance
    Revenue: $12.4M (vs $11.2M target, +10.7%)
    ...

    [Transcript: Board Meeting 2026-05-07]
    [00:03:21] Speaker-1: "The revenue number is strong..."
    ...

  # Structured data (tables, key-value pairs)
  structured_data:
    - source: "input-001"
      type: table
      table_id: "tbl-001"
      headers: [Metric, Q2 Actual, Q2 Target, Variance]
      rows:
        - [Revenue, "$12.4M", "$11.2M", "+10.7%"]

  # Named entities across all inputs
  entities:
    organizations: ["Acme Corp", "Enterprise OS Inc"]
    people: ["Alice Chen", "Bob Smith"]
    dates: ["2026-05-07", "2026-06-30"]
    amounts: ["$12.4M", "$11.2M", "$250K"]
    locations: ["San Francisco"]

  # Action items from audio/video
  action_items:
    - text: "Alice to own the SOC2 evidence collection by end of next week"
      assignee: "Alice Chen"
      due: "2026-05-14"
      source: "input-002"
      timestamp: "00:23:45"

  # Source metadata
  metadata:
    doc_page_count: 24
    audio_duration_seconds: 3240
    speakers_detected: 6
    languages: [en]
    ocr_applied: false
    transcription_confidence_mean: 0.93

  # Search index registration
  index_ref: "enterprise-search/doc/MM-CTX-2026-xxxxx"
  data_classification: INTERNAL
```

---

## Parallel Processing Architecture

```
MULTI-MODAL PROCESSING PIPELINE

Input submission
    │
    ▼
Modality Detection (MIME + extension)
    │
    ├──────────────────────────────────┐
    │  (parallel for each modality)    │
    ▼                                  ▼
document-intelligence          audio-video-processing
(PDF, DOCX, XLSX)              (MP3, MP4, MOV)
    │                                  │
    ├──────── visual-analytics ────────┤
    │        (PNG, JPG, keyframes)     │
    │                                  │
    └──────────────┬───────────────────┘
                   │
                   ▼
        Context Assembly
        (merge all extracts)
                   │
                   ▼
        Enterprise Search Indexing
                   │
                   ▼
        Return unified_context
```

---

## Processing Time Estimates

| Modality | Input Size | Processing Time | Notes |
|----------|-----------|----------------|-------|
| Document (PDF, 10 pages) | ~500KB | 5–15 seconds | Faster without OCR |
| Document (PDF, 100 pages) | ~5MB | 30–90 seconds | Parallel page processing |
| Image (screenshot) | ~200KB | 2–5 seconds | |
| Audio (1 hour meeting) | ~100MB | 10–20 minutes | Transcription + diarization |
| Video (1 hour, 1080p) | ~2GB | 30–60 minutes | Audio + keyframe extraction |

---

## Data Governance Tagging

```yaml
data_governance:
  # Applied automatically based on content analysis
  classification_rules:
    - if: "entities.amounts detected AND source modality == document"
      classification: CONFIDENTIAL
    - if: "entities.people detected AND content_type == hr_document"
      classification: RESTRICTED
    - if: "entities.organizations detected"
      classification: INTERNAL
    - default: INTERNAL

  retention:
    raw_input: 90 days
    processed_context: 365 days
    evidence_artifacts: 7 years  # For compliance-relevant documents
```