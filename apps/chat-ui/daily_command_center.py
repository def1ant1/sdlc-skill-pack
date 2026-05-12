def build_daily_plan(priorities:list[str],blockers:list[str])->dict:
    return {"priorities":priorities,"blockers":blockers,"next_actions":len(priorities)}
