# Conversation Artifact Events Template

Use this template to track stateful artifact activity during orchestration.

```yaml
event_id: evt_<uuid>
timestamp: <iso8601>
conversation_id: <id>
state: <conversation_state>
action: <created|updated|approved|rejected|paused|resumed|forgotten>
artifact:
  id: <artifact_id>
  type: <plan|workflow|knowledge_note|schedule|result_review>
  title: <string>
context:
  goal: <string>
  resolved_questions:
    - <question_key>
  interruption: <none|pause|switch|forget|resume>
metadata:
  actor: <user|assistant|system>
  notes: <string>
```
