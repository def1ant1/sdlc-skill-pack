from pathlib import Path
import subprocess, sys, json

REPO_ROOT = Path(__file__).parent.parent.parent
VALIDATOR = REPO_ROOT / 'scripts' / 'validate_skill_contracts.py'
INVENTORY = REPO_ROOT / 'scripts' / 'generate_skill_inventory.py'

def test_contract_validator_fails_on_missing_fields(tmp_path: Path):
    (tmp_path/'schemas').mkdir(); (tmp_path/'schemas'/'skill-manifest-v9.schema.json').write_text((REPO_ROOT/'schemas'/'skill-manifest-v9.schema.json').read_text())
    d=tmp_path/'skills'/'x'; d.mkdir(parents=True); (d/'SKILL.md').write_text('---\nname: x\n---\n')
    out=subprocess.run([sys.executable,str(VALIDATOR),str(tmp_path)],capture_output=True,text=True)
    assert out.returncode != 0

def test_inventory_deterministic_order(tmp_path: Path):
    for n in ['b-skill','a-skill']:
        d=tmp_path/'skills'/n; d.mkdir(parents=True); (d/'SKILL.md').write_text(f'---\nname: {n}\n---\n')
    subprocess.run([sys.executable,str(INVENTORY),'--root',str(tmp_path)],check=True)
    data=json.loads((tmp_path/'reports'/'skill_inventory.json').read_text())
    assert [r['id'] for r in data]==['a-skill','b-skill']
