def summarize_skill_gaps(findings:list[dict])->dict:
    return {"total":len(findings),"high_value":[f for f in findings if f.get("impact")=="high"]}
