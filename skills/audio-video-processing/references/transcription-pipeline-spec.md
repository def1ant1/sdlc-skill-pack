# Audio-Video Processing — Transcription Pipeline Specification

## Supported Input Formats

| Format | MIME Type | Max Size | Notes |
|--------|-----------|---------|-------|
| MP3 | audio/mpeg | 500 MB | Standard audio |
| WAV | audio/wav | 1 GB | Uncompressed; large files |
| M4A | audio/mp4 | 500 MB | Apple audio |
| MP4 (audio track) | video/mp4 | 5 GB | Audio extracted automatically |
| MOV | video/quicktime | 5 GB | Audio extracted automatically |
| WebM | video/webm | 2 GB | Browser recordings |

---

## Transcription Pipeline

```
Input: audio/video URI
        │
        ▼
1. Audio extraction (if video input)
   └── ffmpeg: extract mono 16kHz WAV for transcription
        │
        ▼
2. Speaker diarization (pre-transcription)
   └── pyannote.audio: identify N speakers; label Speaker-0, Speaker-1, ...
        │
        ▼
3. Transcription (Whisper large-v3 or cloud ASR)
   ├── Chunk audio into 30-second segments for parallel processing
   └── Include timestamps at word level
        │
        ▼
4. Alignment: merge diarization with transcript
   └── Assign speaker labels to each transcript segment
        │
        ▼
5. Post-processing
   ├── Punctuation restoration (if not included by ASR)
   ├── Sentence boundary detection
   └── Filler word removal (optional, configurable)
        │
        ▼
6. Action item extraction (LLM call)
        │
        ▼
7. Meeting summary generation (LLM call)
        │
        ▼
8. Assemble transcript record → return to caller
```

---

## Transcript Record Schema

```yaml
transcript_record:
  transcript_id: "TR-2026-xxxxx"
  source_uri: "s3://apotheon-recordings/board-meeting-2026-05-07.mp4"
  transcribed_at: "2026-05-07T10:20:00Z"

  metadata:
    duration_seconds: 3240
    language: en
    model: whisper-large-v3
    speakers_detected: 6
    transcription_confidence_mean: 0.93
    diarization_applied: true
    filler_words_removed: false

  # Full transcript with speaker + timestamps
  segments:
    - segment_id: "SEG-001"
      speaker: "Speaker-1"
      speaker_name: null          # Resolved via speaker ID if voice profile registered
      start_seconds: 0.0
      end_seconds: 8.4
      text: "Good morning everyone. Let's get started with the Q2 review."
      confidence: 0.97

    - segment_id: "SEG-002"
      speaker: "Speaker-2"
      start_seconds: 8.6
      end_seconds: 24.1
      text: "Thanks Alice. I'll hand over to Bob to walk us through the revenue numbers."
      confidence: 0.95

  # Speaker identification (if voice profiles registered)
  speaker_mapping:
    Speaker-1: "alice-chen"    # Resolved
    Speaker-2: "bob-smith"     # Resolved
    Speaker-3: null            # Unidentified

  # Structured outputs
  action_items:
    - text: "Alice to own the SOC2 evidence collection by end of next week"
      assignee: "Alice Chen"
      due_date: "2026-05-14"
      timestamp_seconds: 1425
      confidence: 0.92

  decisions:
    - text: "Board approves wave-9 go-live for May 14"
      timestamp_seconds: 2100
      confidence: 0.95

  summary: |
    Board meeting covering Q2 financial results (revenue $12.4M, +10.7% vs target),
    wave-9 deployment approval (go-live May 14), and SOC2 status update.
    6 action items assigned. 2 board resolutions passed.

  # Linked entities
  entities_mentioned:
    people: ["Alice Chen", "Bob Smith"]
    organizations: ["Enterprise OS Inc"]
    dates: ["2026-05-14", "2026-06-30"]
    amounts: ["$12.4M", "$250K"]

  data_classification: CONFIDENTIAL
  contains_pii: true
```

---

## Speaker Voice Profile Schema

```yaml
voice_profile:
  profile_id: "VP-2026-xxxxx"
  person_id: "person:alice-chen"
  name: "Alice Chen"
  created_at: "2026-01-10T00:00:00Z"

  enrollment:
    audio_samples: 5
    total_duration_seconds: 120
    enrollment_quality: good   # good | acceptable | poor
    enrolled_by: "alice.chen@example.com"

  model:
    embedding_model: "pyannote-speaker-embedding-v3"
    embedding_vector: [...]     # Stored in vector DB; not serialized here
```

---

## Keyframe Extraction (Video Inputs)

For video inputs, keyframes are extracted for visual-analytics processing:

```yaml
keyframe_extraction:
  strategy: scene_change         # scene_change | fixed_interval | both
  scene_change_threshold: 0.3   # Sensitivity (0=all frames, 1=only major changes)
  fixed_interval_seconds: 60    # Also extract every 60s (max one per minute)
  max_keyframes: 200
  output_format: JPEG
  output_quality: 85

  keyframes:
    - keyframe_id: "KF-001"
      timestamp_seconds: 0.0
      trigger: scene_change
      uri: "gs://apotheon-keyframes/TR-2026-xxxxx/KF-001.jpg"

    - keyframe_id: "KF-002"
      timestamp_seconds: 60.0
      trigger: fixed_interval
      uri: "gs://apotheon-keyframes/TR-2026-xxxxx/KF-002.jpg"
```

---

## Processing Time Estimates

| Input | Duration | Processing Time | Notes |
|-------|----------|----------------|-------|
| Audio (meeting, 1 hour) | 3,600 s | 10–20 min | Diarization adds ~5 min |
| Audio (interview, 30 min) | 1,800 s | 5–10 min | |
| Video (1 hour, 1080p) | 3,600 s | 30–60 min | Audio + keyframe extraction |
| Video (1 hour, 4K) | 3,600 s | 60–120 min | Higher resolution processing |

Processing runs on Ray workers (gpu-workers pool for Whisper inference).

---

## Transcription Quality Targets

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Mean confidence | > 0.90 | < 0.75 |
| Word Error Rate (WER) | < 8% | > 15% |
| Speaker diarization accuracy | > 85% | < 70% |
| Action item recall | > 80% | < 60% |
| Processing latency (1h audio) | < 20 min | > 45 min |