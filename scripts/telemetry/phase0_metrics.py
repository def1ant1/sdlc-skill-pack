#!/usr/bin/env python3
from pathlib import Path
import json
root = Path('.')
metrics = {
  "skills": len(list((root/'skills').glob('*/SKILL.md'))) if (root/'skills').exists() else 0,
  "core_skills": len(list((root/'core').glob('*/SKILL.md'))) if (root/'core').exists() else 0,
  "standards": len(list((root/'shared/standards').glob('*.md'))) if (root/'shared/standards').exists() else 0,
  "policies": len(list((root/'shared/policies').glob('*.md'))) if (root/'shared/policies').exists() else 0,
}
print(json.dumps(metrics, indent=2))
