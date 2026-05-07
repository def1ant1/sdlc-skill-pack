---
name: reasoning-depth-estimation
description: Estimates the reasoning depth required for a given task to enable accurate model tier selection — distinguishing tasks requiring simple lookup from those requiring multi-step chain-of-thought or formal reasoning.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: platform
  maturity: alpha
  dependencies: [model-routing, model-selection-optimization, telemetry]
---

## Role

Reasoning depth estimation specialist. Analyzes incoming task requests to predict the
cognitive depth required — simple retrieval, structured reasoning, or deep chain-of-thought
— enabling model-routing to select the minimum-sufficient model tier without sacrificing quality.

## Activation Triggers

- Inference request received with unclassified complexity
- Model-routing requires depth estimate for tier selection
- Historical routing data shows systematic over- or under-routing
- New task type added requiring calibration

## Execution Protocol

1. **Analyze task features**: Extract features from the task: input length, output type, task
   keywords, number of logical steps implied, presence of mathematical or formal content.

2. **Apply heuristic classifier**: Score task on reasoning depth scale 0-10:
   (0-2: retrieval/classification, 3-5: summarization/analysis, 6-8: multi-step reasoning,
   9-10: formal/mathematical/planning).

3. **Check against similar tasks**: Query routing history for tasks with similar features;
   compute median model tier used and quality score achieved.

4. **Estimate chain-of-thought requirement**: Detect indicators of CoT need: mathematical
   symbols, logical connectors, multi-part questions, ambiguous premises.

5. **Output depth estimate**: Return estimated depth score (0-10), recommended minimum model
   tier, and confidence level (high/medium/low based on feature signal strength).

6. **Update calibration data**: Record estimation vs. actual outcome (quality score and model
   used) to improve future estimations via feedback loop.

## Output Format

Depth estimation result with: depth score (0-10), reasoning category, recommended model tier,
confidence level, key features driving the estimate, and similar historical task references.

## References

- `references/depth-estimation-heuristics.md` — feature extraction rules, depth score anchors, model tier mapping, calibration methodology