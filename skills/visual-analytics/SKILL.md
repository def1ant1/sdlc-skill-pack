---
name: visual-analytics
description: Interprets charts, dashboard screenshots, and diagrams as structured enterprise intelligence for the multi-modal processing pipeline.
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

Visual content understanding skill. Takes images (charts, dashboards, screenshots, diagrams,
whiteboards) and produces structured descriptions and extracted data that downstream agents
can reason over. Bridges the gap between visual enterprise content and the platform's
text-and-data reasoning capabilities.

## Activation Triggers

- `multimodal-runtime` routes an image input for visual analysis
- A dashboard screenshot requires metric extraction for automated reporting
- An architecture diagram requires component and relationship extraction
- A chart or graph requires data extraction for numerical analysis
- An operator submits a visual artifact for intelligence extraction

## Execution Protocol

1. **Image classification**: Identify the visual content type:
   `chart` | `dashboard` | `architecture_diagram` | `whiteboard` | `screenshot` | `photo`

2. **Content extraction by type**:

   **Charts** (bar, line, pie, scatter, heatmap):
   - Extract axis labels, legend labels, data series names
   - Estimate data values from visual position (pixel-to-value mapping)
   - Identify trend direction (up/down/flat) for line charts
   - Output: structured data table approximation

   **Dashboards**:
   - Identify KPI panels and extract metric names and values (text extraction via OCR)
   - Identify status indicators (red/amber/green) and their associated metrics
   - Output: KPI table with name, value, status

   **Architecture diagrams**:
   - Identify component boxes and their labels
   - Identify connections/arrows and their direction
   - Output: node list + edge list (informal graph representation)

   **Whiteboards**:
   - OCR text recognition for written content
   - Shape detection (boxes, circles, arrows)
   - Output: annotated description of whiteboard content

3. **Confidence annotation**: For all extracted values, annotate with confidence level
   (high / medium / low) based on image clarity and extraction certainty.

4. **Natural language summary**: Generate a 3–5 sentence plain-English description of
   what the visual shows and any notable patterns or anomalies.

## Output Format

```yaml
visual_analysis:
  image_id: "VIS-2026-xxxxx"
  content_type: chart | dashboard | architecture_diagram | whiteboard | screenshot
  extracted_data: {}
  summary: "The line chart shows API latency trending upward over the last 7 days, with a notable spike on May 5th reaching 850ms p95."
  confidence_overall: high | medium | low
  requires_human_review: false
```

## Quality Gates

- Low confidence extractions must be flagged — do not present as authoritative data
- Chart data extraction error margin must be disclosed (pixel-based approximation)

## References

- `references/` — Content type classification taxonomy, extraction method per chart type, confidence scoring
