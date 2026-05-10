#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

PHASES={103,104,105,107,108,109,110,111,112}
ROOT=Path(__file__).resolve().parents[2]
SKILLS=ROOT/'skills'


def main()->int:
    errs=[]
    for d in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        mf=d/'manifest.v9.json'
        if not mf.exists():
            continue
        m=json.loads(mf.read_text())
        if m.get('subdomain','').startswith('phase-'):
            try: phase=int(m['subdomain'].split('-')[1])
            except Exception: continue
            if phase in PHASES:
                for k in ['token_budget','context_loading','input_contract','output_contract','governance_level','telemetry_events','eval_metrics','failure_modes','fallbacks']:
                    if k not in m:
                        errs.append(f"{mf}: missing {k}")
                if m.get('output_contract',{}).get('format')!='canonical-entity-event-bundle':
                    errs.append(f"{mf}: output_contract.format must be canonical-entity-event-bundle")
                events=set(m.get('telemetry_events',[]))
                if 'policy_gate_checked' not in events:
                    errs.append(f"{mf}: telemetry_events missing policy_gate_checked")
                gate=m.get('human_approval_required')
                is_external='external' in json.dumps(m.get('output_contract',{})) or 'customer' in d.name
                if is_external and gate is not True:
                    errs.append(f"{mf}: external/customer skill must enforce human_approval_required=true")
                for req in [d/'SKILL.md',d/'routing.yaml',d/'examples'/'workflow.yaml']:
                    if not req.exists():
                        errs.append(f"{req}: missing required artifact")
    if errs:
        print('\n'.join(errs))
        return 1
    print('Business skill pack validation passed.')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
