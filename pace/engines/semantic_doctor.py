"""PACE Semantic Doctor (pace doctor --deep).

The Kernel answers a structural question: does the required shape exist?
The semantic Doctor answers a deeper one: does the content hang together?
It checks that active pointers resolve to real files, that supersede
chains are not dangling, that mission/vision/roadmap are no longer
placeholders, that every cited RULE-/DECISION- has a matching file, and
that a ROOT_AUTHORITY is actually named. It returns a list of issues;
an empty list means the instance is semantically coherent. These are
advisory findings layered on top of structural validity, never a
replacement for it.
"""

import re
from pathlib import Path

from pace.services.pdl import read_pdl

PLACEHOLDER = "Not yet defined."
_REF_RE = re.compile(r"\b(RULE|DECISION)-(\d{3,})")


def _known_ids(root: Path) -> set:
    known = set()
    for folder, prefix in (("rules", "RULE"), ("decisions", "DECISION")):
        for f in (root / folder).glob(f"{prefix}-*.pdl"):
            parts = f.stem.split("-")
            if len(parts) >= 2:
                known.add(f"{parts[0]}-{parts[1]}")
    return known


def semantic_check(root: Path) -> list:
    root = Path(root)
    issues = []

    active_file = root / "ACTIVE_VERSIONS.pdl"
    active = read_pdl(active_file) if active_file.is_file() else {}

    # 1. Active pointers must resolve to real files.
    for key in ("ACTIVE_MISSION", "ACTIVE_VISION", "ACTIVE_ROADMAP", "ACTIVE_SPRINT"):
        rel = active.get(key)
        if rel and not (root / rel).is_file():
            issues.append(f"{key} points to a missing file: {rel}")

    # 2. Supersede chains must not be dangling.
    for pdl in sorted(root.glob("*/*.pdl")):
        sup = read_pdl(pdl).get("SUPERSEDES", "")
        if sup and sup.endswith(".pdl") and not (pdl.parent / sup).is_file():
            issues.append(f"{pdl.parent.name}/{pdl.name} supersedes a missing file: {sup}")

    # 3. Active mission/vision/roadmap must not still be placeholders.
    #    Detect by the literal placeholder text in the raw file, not via the
    #    flat parser: real sections carry multi-line prose the single-line
    #    PDL reader does not capture, so parsing the field would misfire.
    for key, label in (("ACTIVE_MISSION", "mission"), ("ACTIVE_VISION", "vision"), ("ACTIVE_ROADMAP", "roadmap")):
        rel = active.get(key)
        if rel and (root / rel).is_file():
            if PLACEHOLDER in (root / rel).read_text(encoding="utf-8"):
                issues.append(f"{label} is still a placeholder (not yet defined)")

    # 4. Every cited RULE-/DECISION- must have a matching file.
    known = _known_ids(root)
    cited = set()
    for pdl in root.glob("*/*.pdl"):
        for kind, num in _REF_RE.findall(pdl.read_text(encoding="utf-8")):
            cited.add(f"{kind}-{num}")
    for ref in sorted(cited):
        if ref not in known:
            where = "rules" if ref.startswith("RULE") else "decisions"
            issues.append(f"{ref} is cited but has no matching file in .pace/{where}/")

    # 5. A ROOT_AUTHORITY must actually be named.
    actors_dir = root / "actors"
    has_root = any(
        read_pdl(a).get("IS_ROOT_AUTHORITY", "").lower() == "true"
        for a in actors_dir.glob("ACTOR-*.pdl")
    ) if actors_dir.is_dir() else False
    if not has_root:
        issues.append("no ROOT_AUTHORITY named (no actor with IS_ROOT_AUTHORITY true) - governance incomplete")

    return issues
