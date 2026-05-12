#!/usr/bin/env python3
"""Conversation -> knowledge note proposals with lifecycle operations.

This tool proposes memories instead of auto-persisting every extracted claim.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any


TRIGGERS = {
    "remember": re.compile(r"\bremember this\b", re.IGNORECASE),
    "deprecate": re.compile(r"\bdon[’']?t use that anymore\b", re.IGNORECASE),
}


@dataclass
class Provenance:
    conversation_id: str
    message_refs: list[dict[str, str]] = field(default_factory=list)


@dataclass
class KnowledgeNote:
    id: str
    title: str
    category: str
    status: str
    statement: str
    confidence: str
    staleness: str
    provenance: Provenance
    impact_links: dict[str, list[dict[str, str]]]
    lifecycle: dict[str, Any]


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _note_id() -> str:
    return f"kn-{int(dt.datetime.now().timestamp())}"


def _categorize(text: str) -> str:
    low = text.lower()
    if any(k in low for k in ["must", "required", "cannot", "never"]):
        return "constraint"
    if any(k in low for k in ["prefer", "style", "format"]):
        return "preference"
    if any(k in low for k in ["decide", "decision", "chose", "approved"]):
        return "decision"
    if any(k in low for k in ["steps", "process", "procedure"]):
        return "procedure"
    if any(k in low for k in ["avoid", "deprecated", "unsafe"]):
        return "warning"
    return "fact"


def _sentences(conversation: str) -> list[str]:
    return [s.strip() for s in re.split(r"[\n.!?]", conversation) if len(s.strip()) > 20]


def propose_notes(conversation: str, conversation_id: str, artifacts: list[str], entities: list[str]) -> dict[str, Any]:
    now = _now()
    remember = bool(TRIGGERS["remember"].search(conversation))
    deprecate = bool(TRIGGERS["deprecate"].search(conversation))

    proposals: list[KnowledgeNote] = []
    for idx, sentence in enumerate(_sentences(conversation), start=1):
        note = KnowledgeNote(
            id=f"{_note_id()}-{idx}",
            title=sentence[:64],
            category=_categorize(sentence),
            status="proposed",
            statement=sentence,
            confidence="medium",
            staleness="fresh",
            provenance=Provenance(
                conversation_id=conversation_id,
                message_refs=[{"role": "user", "timestamp": now, "excerpt": sentence[:140]}],
            ),
            impact_links={
                "artifacts": [{"type": "artifact", "id": a} for a in artifacts],
                "entities": [{"type": "entity", "id": e} for e in entities],
            },
            lifecycle={"created_at": now, "updated_at": now, "approved_at": None, "archived_at": None, "superseded_by": None, "history": []},
        )
        proposals.append(note)

    return {
        "conversation_id": conversation_id,
        "mode": "propose_only",
        "commands": {"remember_this_detected": remember, "dont_use_anymore_detected": deprecate},
        "proposals": [asdict(p) for p in proposals],
        "next_actions": ["approve", "edit", "reject", "archive", "supersede"],
    }


def apply_action(note: dict[str, Any], action: str, *, editor: str = "human", replacement_note_id: str | None = None, edited_statement: str | None = None) -> dict[str, Any]:
    now = _now()
    allowed = {"approve", "edit", "reject", "archive", "supersede"}
    if action not in allowed:
        raise ValueError(f"unsupported action: {action}")

    note.setdefault("lifecycle", {}).setdefault("history", []).append({"action": action, "at": now, "by": editor})
    note["lifecycle"]["updated_at"] = now

    if action == "approve":
        note["status"] = "approved"
        note["lifecycle"]["approved_at"] = now
    elif action == "edit":
        note["status"] = "edited"
        if edited_statement:
            note["statement"] = edited_statement
    elif action == "reject":
        note["status"] = "rejected"
    elif action == "archive":
        note["status"] = "archived"
        note["lifecycle"]["archived_at"] = now
    elif action == "supersede":
        note["status"] = "superseded"
        note["lifecycle"]["superseded_by"] = replacement_note_id
        note["staleness"] = "stale"
    return note


def detect_conflicts_and_staleness(notes: list[dict[str, Any]]) -> dict[str, Any]:
    conflicts: list[dict[str, str]] = []
    for i, a in enumerate(notes):
        sa = a.get("statement", "").lower()
        for b in notes[i + 1 :]:
            sb = b.get("statement", "").lower()
            if any(token in sa and f"not {token}" in sb for token in ["use", "enable", "allow"]):
                conflicts.append({"a": a.get("id", ""), "b": b.get("id", ""), "reason": "contradictory polarity detected"})
                a["staleness"] = "conflicted"
                b["staleness"] = "conflicted"
    stale = [n.get("id", "") for n in notes if n.get("status") in {"archived", "superseded"}]
    return {"conflicts": conflicts, "stale_notes": stale}


def _extract_notes(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("proposals"), list):
        return payload["proposals"]
    raise ValueError("notes payload must be a list or an object with `proposals`")


def retrieve_notes(notes: list[dict[str, Any]], *, query: str = "", category: str | None = None, entity: str | None = None) -> list[dict[str, Any]]:
    q = query.lower().strip()
    out = []
    for note in notes:
        if note.get("status") not in {"approved", "edited", "proposed"}:
            continue
        if category and note.get("category") != category:
            continue
        if entity:
            linked = [e.get("id") for e in note.get("impact_links", {}).get("entities", [])]
            if entity not in linked:
                continue
        hay = f"{note.get('title','')} {note.get('statement','')}".lower()
        if q and q not in hay:
            continue
        out.append(note)
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("propose")
    pp.add_argument("--conversation", default="")
    pp.add_argument("--stdin", action="store_true")
    pp.add_argument("--conversation-id", default="conversation-1")
    pp.add_argument("--artifacts", nargs="*", default=[])
    pp.add_argument("--entities", nargs="*", default=[])
    pp.add_argument("--output", type=Path, required=True)

    pa = sub.add_parser("apply-action")
    pa.add_argument("--note", type=Path, required=True)
    pa.add_argument("--action", required=True)
    pa.add_argument("--editor", default="human")
    pa.add_argument("--replacement-note-id")
    pa.add_argument("--edited-statement")
    pa.add_argument("--output", type=Path, required=True)

    pc = sub.add_parser("check")
    pc.add_argument("--notes", type=Path, required=True)
    pc.add_argument("--output", type=Path, required=True)

    pr = sub.add_parser("retrieve")
    pr.add_argument("--notes", type=Path, required=True)
    pr.add_argument("--query", default="")
    pr.add_argument("--category")
    pr.add_argument("--entity")
    pr.add_argument("--output", type=Path, required=True)

    args = p.parse_args()
    if args.cmd == "propose":
        conversation = args.conversation
        if args.stdin or not conversation:
            import sys
            conversation = sys.stdin.read().strip()
        payload = propose_notes(conversation, args.conversation_id, args.artifacts, args.entities)
    elif args.cmd == "apply-action":
        note = json.loads(args.note.read_text(encoding="utf-8"))
        payload = apply_action(note, args.action, editor=args.editor, replacement_note_id=args.replacement_note_id, edited_statement=args.edited_statement)
    elif args.cmd == "check":
        notes = _extract_notes(json.loads(args.notes.read_text(encoding="utf-8")))
        payload = detect_conflicts_and_staleness(notes)
    else:
        notes = _extract_notes(json.loads(args.notes.read_text(encoding="utf-8")))
        payload = retrieve_notes(notes, query=args.query, category=args.category, entity=args.entity)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
