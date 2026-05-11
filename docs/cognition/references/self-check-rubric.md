# Domain Cognition Self-Check Rubric

Use this rubric before emitting a final answer, recommendation, or action plan.

## Scoring
- Score each dimension 0-2.
- 0 = missing/unsafe, 1 = partial, 2 = complete.
- Minimum ship threshold: 14/18 overall and no 0 in Policy, Evidence, or Risk.

## Dimensions
1. **Problem framing**: objective, scope, and constraints are explicit.
2. **Domain principles fit**: recommendation follows module principles.
3. **Heuristic quality**: heuristics applied and trade-offs acknowledged.
4. **Framework completeness**: required framework steps are covered.
5. **Evaluator pass**: domain evaluator checks are met.
6. **Anti-pattern scan**: anti-pattern detectors were run and resolved.
7. **Policy boundary compliance**: output stays within professional-advice and approval boundaries.
8. **Memory hygiene**: stable facts, assumptions, and open risks are captured as memory hooks.
9. **Actionability**: next actions, owners, and checkpoints are concrete.

## Output footer template
```yaml
self_check:
  rubric_version: cognition-rubric-v1
  score_total: <0-18>
  blocked: <true|false>
  blocking_reasons: [ ... ]
  improvements: [ ... ]
```
