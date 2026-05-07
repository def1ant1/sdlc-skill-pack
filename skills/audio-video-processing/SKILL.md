---
name: audio-video-processing
description: Transcribes audio, performs speaker diarization, and analyzes video frames for enterprise content.
metadata:
  version: "0.1.0"
  category: multimodal
  owner: platform
  maturity: draft
  dependencies: ['multimodal-runtime']
---

## Role

Transcribes audio, performs speaker diarization, and analyzes video frames for enterprise content.

## Activation Triggers

- Invoked by `sdlc-orchestration` when the objective requires audio video processing capability
- Called by orchestration plan referencing this skill as a required step

## Execution Protocol

1. **Receive task context**: Parse the skill invocation payload and validate required fields.
2. **Execute skill workflow**: Apply the domain-specific logic documented in `references/`.
3. **Validate outputs**: Check outputs against quality gates before returning.
4. **Return result**: Emit structured output and telemetry.

## Output Format

```yaml
result:
  status: success | partial | failed
  skill: audio-video-processing
  outputs: {}
  quality_gates_passed: true
```

## References

- `references/` — Domain-specific methodology, schemas, and standards
