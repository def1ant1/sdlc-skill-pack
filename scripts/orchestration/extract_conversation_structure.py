#!/usr/bin/env python3
"""Extract and review conversation structure before persistence."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from typing import Any

BUCKETS = ["requirements", "risks", "decisions", "tasks", "entities"]


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: str, payload: Any) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def derive_suggestions(messages: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Minimal deterministic extraction stub keyed off message tags.

    Upstream LLM extraction can replace this function while preserving review mechanics.
    """
    extracted = {bucket: [] for bucket in BUCKETS}
    for message in messages:
        tags = message.get("tags", [])
        msg_id = message.get("id", "unknown")
        text = message.get("text", "")
        for tag in tags:
            if tag in extracted:
                extracted[tag].append(
                    {
                        "suggestion_id": f"{tag[:3]}-{msg_id}",
                        "title": text[:80] if tag in {"requirements", "tasks"} else None,
                        "description": text if tag == "requirements" else None,
                        "statement": text if tag == "risks" else None,
                        "question": text if tag == "decisions" else None,
                        "name": text[:80] if tag == "entities" else None,
                        "source_message_ids": [msg_id],
                        "review_status": "suggested",
                    }
                )
    return extracted


def strip_none(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: strip_none(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [strip_none(item) for item in obj]
    return obj


def index_suggestions(payload: dict[str, Any]) -> dict[str, tuple[str, int]]:
    idx = {}
    for bucket in BUCKETS:
        for position, item in enumerate(payload.get(bucket, [])):
            idx[item["suggestion_id"]] = (bucket, position)
    return idx


def apply_actions(result: dict[str, Any], actions: list[dict[str, Any]]) -> dict[str, Any]:
    updated = copy.deepcopy(result)
    review_log = updated.setdefault("review_log", [])

    for action in actions:
        act = action["action"]
        suggestion_id = action["suggestion_id"]
        idx = index_suggestions(updated)
        if suggestion_id not in idx:
            raise ValueError(f"Unknown suggestion_id: {suggestion_id}")
        bucket, position = idx[suggestion_id]
        item = updated[bucket][position]

        if act == "approve":
            item["review_status"] = "approved"
        elif act == "reject":
            item["review_status"] = "rejected"
        elif act == "edit":
            patch = action.get("patch", {})
            item.update(patch)
            item["review_status"] = "edited"
        elif act == "merge":
            merge_target = action.get("merge_into")
            if not merge_target or merge_target not in idx:
                raise ValueError(f"Invalid merge target: {merge_target}")
            target_bucket, target_position = idx[merge_target]
            target = updated[target_bucket][target_position]
            if target_bucket != bucket:
                raise ValueError("merge requires same-type suggestions")
            target_sources = set(target.get("source_message_ids", []))
            target_sources.update(item.get("source_message_ids", []))
            target["source_message_ids"] = sorted(target_sources)
            target.setdefault("merged_suggestion_ids", []).append(suggestion_id)
            item["review_status"] = "merged"
        else:
            raise ValueError(f"Unsupported action: {act}")

        review_log.append(
            {
                "action": act,
                "suggestion_id": suggestion_id,
                "merged_into": action.get("merge_into"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "note": action.get("note"),
            }
        )

    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--messages", required=True, help="Input conversation messages JSON file")
    parser.add_argument("--actions", help="Optional review actions JSON file")
    parser.add_argument("--output", help="Output file for final extraction result")
    parser.add_argument("--conversation-id", default="conversation-unknown")
    args = parser.parse_args()

    messages = load_json(args.messages)
    suggestions = derive_suggestions(messages)
    result = {
        "conversation_id": args.conversation_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        **strip_none(suggestions),
    }

    print("# Review suggestions before persistence")
    print(json.dumps(result, indent=2))

    if args.actions:
        actions = load_json(args.actions)
        result = apply_actions(result, actions)

    if args.output:
        save_json(args.output, result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
