#!/usr/bin/env python3
from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path
CATEGORIES=["workflow lifecycle","retries","circuit/open health","misfires","HITL","policy","schema failures"]
def categorize(name:str)->str:
 n=name.lower()
 if 'retry' in n:return 'retries'
 if 'circuit' in n:return 'circuit/open health'
 if 'misfire' in n:return 'misfires'
 if 'hitl' in n:return 'HITL'
 if 'policy' in n:return 'policy'
 if 'schema' in n or 'validation' in n:return 'schema failures'
 return 'workflow lifecycle'
def generate(telemetry_path:Path)->dict:
 events=[]
 if telemetry_path.exists():
  for line in telemetry_path.read_text(encoding='utf-8').splitlines():
   line=line.strip()
   if not line or line=='---':continue
   try:events.append(json.loads(line))
   except Exception:continue
 counts=Counter(categorize(e.get('event_name','')) for e in events)
 failures=defaultdict(list)
 for e in events:
  if str(e.get('status','')).lower() in {'error','failed','fail'}:
   failures[categorize(e.get('event_name',''))].append(e)
 rem={c:("Review logs and retry failed runs." if failures[c] else "No remediation required.") for c in CATEGORIES}
 return {"totals":dict(counts),"failure_categories":{k:len(v) for k,v in failures.items()},"remediation":rem,"events":events}
def main()->int:
 root=Path(__file__).resolve().parents[2]
 data=generate(root/'telemetry.log.yaml')
 (root/'reports'/'runtime_diagnostics.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 lines=['# Runtime Diagnostics','','## Failure Aggregation']
 for c in CATEGORIES: lines.append(f"- {c}: {data['failure_categories'].get(c,0)} failures — {data['remediation'][c]}")
 (root/'reports'/'runtime_diagnostics.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 return 0
if __name__=='__main__': raise SystemExit(main())
