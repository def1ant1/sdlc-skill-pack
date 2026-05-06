#!/usr/bin/env python3
"""Validate a minimal workflow state object."""
import json, sys
required = ["objective", "current_phase", "required_skills", "deliverables", "quality_gates"]
data = json.load(sys.stdin)
missing = [k for k in required if k not in data]
if missing:
    print(json.dumps({"valid": False, "missing": missing}, indent=2))
    sys.exit(1)
print(json.dumps({"valid": True}, indent=2))
