def validate_accessibility_metadata(component):
    missing=[k for k in ["aria_label","role","tab_index"] if k not in component]
    return {"valid": not missing, "missing": missing}
