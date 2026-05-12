def build_decision_record(options:list[dict])->dict:
    return {"options": options, "confidence": min((o.get("confidence",1) for o in options), default=1), "provenance": sorted({p for o in options for p in o.get("provenance",[])}), "linked_artifacts": sorted({a for o in options for a in o.get("linked_artifacts",[])})}
