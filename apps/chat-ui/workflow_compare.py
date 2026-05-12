"""Workflow comparison surface."""

def compare_workflows(left: dict, right: dict) -> dict:
    return {"left": left.get("id"), "right": right.get("id"), "confidence": min(left.get("confidence",1), right.get("confidence",1)), "provenance": sorted(set(left.get("provenance",[])+right.get("provenance",[]))), "linked_artifacts": sorted(set(left.get("linked_artifacts",[])+right.get("linked_artifacts",[])))}
