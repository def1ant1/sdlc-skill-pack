#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validation.validate_json_schema import load_doc, validate  # noqa: E402

EXAMPLES = ROOT / "examples" / "events"


def main() -> int:
    if not EXAMPLES.exists():
        print("No event payload examples found; skipping.")
        return 0

    failures: list[str] = []
    for sample in sorted(EXAMPLES.glob("*.json")):
        doc = load_doc(sample)
        schema_ref = doc.get("$schema_ref")
        if not schema_ref:
            failures.append(f"{sample}: $.$schema_ref missing required field")
            continue
        schema_path = (ROOT / schema_ref).resolve()
        if not schema_path.exists():
            failures.append(f"{sample}: $.$schema_ref points to missing schema {schema_ref}")
            continue
        schema = json.loads(schema_path.read_text())
        errs = validate(doc, schema, strict=True)
        if "source" not in doc:
            failures.append(f"{sample}: $.source missing required field")
        failures.extend([f"{sample}: {e}" for e in errs])

    if failures:
        print("\n".join(failures))
        return 1
    print("Event payload schema validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
