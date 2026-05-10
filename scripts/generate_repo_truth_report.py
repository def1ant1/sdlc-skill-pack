#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path.cwd()); args=ap.parse_args(); root=args.root
    refs=json.loads(subprocess.run([sys.executable,str(root/'scripts'/'extract_backlog_paths.py'),'--root',str(root)],capture_output=True,text=True,check=True).stdout)
    val=subprocess.run([sys.executable,str(root/'scripts'/'validate_backlog_truth.py'),'--root',str(root)],capture_output=True,text=True)
    missing=[]
    for line in val.stdout.splitlines():
        if line.startswith('- '): missing.append(line[2:])
    report={"reference_count":len(refs),"missing_count":len(missing),"status":"pass" if val.returncode==0 else "fail","missing":missing}
    (root/'reports').mkdir(exist_ok=True)
    (root/'reports'/'repo_truth_report.json').write_text(json.dumps(report,indent=2)+"\n",encoding='utf-8')
    md=["# Repo Truth Report","",f"Status: **{report['status'].upper()}**",f"","- Total references: {len(refs)}",f"- Missing references: {len(missing)}",""]
    if missing: md += ["## Missing Paths",""]+[f"- {m}" for m in missing]
    (root/'reports'/'repo_truth_report.md').write_text("\n".join(md)+"\n",encoding='utf-8')
    print('Generated reports/repo_truth_report.md and reports/repo_truth_report.json')
    return 0
if __name__=='__main__': raise SystemExit(main())
