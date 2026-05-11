#!/usr/bin/env python3
from __future__ import annotations
import json
from scripts.schedules.preview_schedule import load_registry
print(json.dumps({'schedules':load_registry()}, indent=2, sort_keys=True))
