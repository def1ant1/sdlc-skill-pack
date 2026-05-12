#!/usr/bin/env python3
"""Generate next-best actions from workspace signals."""
import json

actions=[{"id":"nba-1","title":"Unblock stalled roadmap milestone","expected_impact":"Restore delivery flow","effort":"medium","urgency":"high","confidence":0.84,"provenance":["tasks/T-120","workflows/WF-44"],"linked_artifacts":["plans/Q3-roadmap.md"]}]
print(json.dumps(actions,indent=2))
