# Memory Packet Schema

```yaml
memory_packet:
  project:
    name:
    domain:
    objective:
  phase:
    current:
    previous:
    next:
  decisions:
    accepted: []
    rejected: []
    pending: []
  constraints:
    business: []
    technical: []
    security: []
    compliance: []
  artifacts:
    created: []
    modified: []
    required: []
  quality:
    risks: []
    tests_needed: []
    review_required: []
  context:
    summary:
    unresolved_questions: []
    next_action:
```
