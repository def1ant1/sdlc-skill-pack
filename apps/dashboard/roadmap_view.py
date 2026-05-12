"""Roadmap planning view."""

def summarize_roadmap(items:list[dict])->dict:
    return {"count":len(items),"views":["weekly","monthly","quarterly"]}
