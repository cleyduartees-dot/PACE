"""Decisions engine - record an approved decision the moment it is made,
so it never lives only in the chat (REQUEST-0016 / RULE-0008).

`capture_decision` is the conversational-capture verb: an AI calls it the
instant the owner approves something, writing a DECISION-NNNN into
.pace/decisions/ with the next correlative. Append-only, like the other
protected records.
"""

from datetime import datetime, timezone
from pathlib import Path

DECISIONS_DIR = "decisions"


def _next_id(directory: Path) -> int:
    n = 0
    if directory.is_dir():
        for p in directory.glob("DECISION-*.pdl"):
            parts = p.stem.split("-")
            if len(parts) >= 2 and parts[1].isdigit():
                n = max(n, int(parts[1]))
    return n + 1


def _slug(text: str) -> str:
    slug = "".join(c if c.isalnum() else "-" for c in text.lower())
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")[:48] or "decision"


def capture_decision(root, title, detail="", decided_by=""):
    if not title.strip():
        raise ValueError("a decision needs a non-empty title")
    directory = Path(root) / DECISIONS_DIR
    directory.mkdir(parents=True, exist_ok=True)
    num = _next_id(directory)
    did = f"DECISION-{num:04d}"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    fields = {
        "DECISION_VERSION": "1.0.0",
        "ID": did,
        "STATUS": "APPROVED",
        "DATE": stamp,
        "DECIDED_BY": decided_by or "(project owner)",
        "TITLE": title,
    }
    if detail:
        fields["RATIONALE"] = detail
    fields["RAW_TEXT"] = title
    lines = [f"{k} {v}".rstrip() for k, v in fields.items()]
    lines.append("END")
    path = directory / f"{did}-{_slug(title)}.pdl"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
