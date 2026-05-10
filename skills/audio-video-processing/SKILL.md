---
name: audio-video-processing
description: Transcribes enterprise audio recordings, performs speaker diarization, and analyzes video frames for meeting intelligence and content understanding.
metadata:
  version: "0.1.0"
  category: multimodal
  owner: platform
  maturity: draft
  dependencies: ['multimodal-runtime']

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

Enterprise audio and video intelligence skill. Processes meeting recordings, call recordings,
video presentations, and surveillance footage to extract structured intelligence: transcriptions,
speaker-attributed dialogue, action items, decisions, and video frame content descriptions.

## Activation Triggers

- `multimodal-runtime` routes an audio or video input for processing
- A meeting recording is ingested from a conferencing system (Zoom, Teams, Meet)
- A video presentation or training recording requires content extraction
- An operator submits an audio/video file for intelligence extraction

## Execution Protocol

1. **Format handling**: Accept audio (MP3, WAV, M4A, OGG, FLAC) and video (MP4, MOV, AVI, MKV).
   For video: extract audio track + keyframe images at 1-per-second interval.

2. **Transcription**: Run automatic speech recognition (ASR) on the audio track.
   Output: word-level timestamps, confidence scores, language detection.

3. **Speaker diarization**: Identify distinct speakers in the recording.
   Output: speaker segments with `speaker_id` (anonymous labels: Speaker-1, Speaker-2),
   start/end timestamps per segment.

4. **Speaker-attributed transcript**: Merge transcription and diarization into a
   structured dialogue format:
   ```
   [00:01:32] Speaker-1: "We should prioritize the compliance gate before the Q3 launch."
   [00:01:45] Speaker-2: "Agreed. Can you own the SOC2 evidence collection?"
   ```

5. **Content intelligence** (for meeting recordings):
   - **Action item extraction**: identify sentences with commitment language ("I will", "we'll", "by Friday")
   - **Decision extraction**: identify resolution sentences ("we decided", "the plan is", "approved")
   - **Topic segmentation**: group transcript into topic segments with labels

6. **Video frame analysis** (for video inputs):
   Route keyframe images to `visual-analytics` for content description.
   Merge frame descriptions with the transcript timeline.

## Output Format

```yaml
av_processing:
  media_id: "AV-2026-xxxxx"
  duration_seconds: 0
  language_detected: en
  speakers_detected: 0
  transcript_word_count: 0
  action_items: []
  decisions: []
  topics: []
  video_frame_count: 0
  confidence_mean: 0.0
```

## Quality Gates

- Transcription confidence mean < 0.80 → flag for human review
- Speaker diarization: flag segments with overlapping speakers for manual attribution

## References

- `references/` — ASR model selection, diarization algorithm, action item extraction patterns
