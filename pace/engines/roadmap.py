"""Roadmap engine - turn the prose roadmap into DATA, and detect drift
between the roadmap and an external task tracker (ClickUp/Jira export).

Local, dependency-free half of the ClickUp/GitHub connector (REQUEST-0011)
and the automated remedy to RULE-0010: instead of trusting the AI to
remember, PACE can be handed a tracker snapshot and report which roadmap
items are missing from the board or whose status disagrees. Live
authenticated API access is a separate future/cloud concern.
"""

import re
from pathlib import Path

from pace.services.pdl import read_pdl

_ITEM = re.compile(r"^\s+(\d{2})\s+(.*\S)\s*$")
_DONE_MARKERS = ("[DONE", "[COMPLETE")  # prefix match: [DONE], [DONE - x], [COMPLETE]
_DONE_STATUSES = {"complete", "completed", "done", "closed"}


def _active_roadmap_text(root):
    active = read_pdl(Path(root) / "ACTIVE_VERSIONS.pdl")
    return (Path(root) / active["ACTIVE_ROADMAP"]).read_text(encoding="utf-8")


def _is_done(text):
    up = text.upper()
    return any(marker in up for marker in _DONE_MARKERS)


def parse_roadmap(root):
    items = []
    phase = None
    phase_done = False
    for line in _active_roadmap_text(root).splitlines():
        stripped = line.strip()
        if stripped.startswith("PHASE_"):
            phase = stripped.split("--")[0].strip()
            phase_done = _is_done(stripped)
            continue
        m = _ITEM.match(line)
        if m:
            number, title = m.group(1), m.group(2)
            done = _is_done(title) or phase_done
            items.append({"phase": phase, "number": number, "title": title, "done": done})
    return items


def _number_from_name(name):
    m = re.search(r"(\d{2})", str(name))
    return m.group(1) if m else None


def drift(items, tracker_tasks):
    tmap = {}
    for t in tracker_tasks:
        num = t.get("number") or _number_from_name(t.get("name", ""))
        if num:
            tmap[num] = t
    missing, mismatch = [], []
    for it in items:
        t = tmap.get(it["number"])
        if t is None:
            missing.append(it["number"])
            continue
        tracker_done = str(t.get("status", "")).lower() in _DONE_STATUSES
        if tracker_done != it["done"]:
            mismatch.append({
                "number": it["number"],
                "roadmap_done": it["done"],
                "tracker_status": t.get("status"),
            })
    return {"missing": missing, "status_mismatch": mismatch}
