"""Rules engine - the approved, permanent governance rules an AI must obey.

Each rule is a RULE-NNNN.pdl file in .pace/rules/, scoped PACE / ORGANIZATION
/ PROJECT. Rules are how an approved correction stops being a one-off and
becomes something no AI has to be told twice. Append-only: a rule is
superseded by a new file, never edited in place.
"""

from datetime import datetime, timezone
from pathlib import Path

from pace.services.pdl import read_pdl

RULES_DIR = "rules"
VALID_SCOPES = ("PACE", "ORGANIZATION", "PROJECT")


def _rules_dir(root: Path) -> Path:
    return Path(root) / RULES_DIR


def _next_id(directory: Path) -> str:
    n = 0
    if directory.is_dir():
        for p in directory.glob("RULE-*.pdl"):
            parts = p.stem.split("-")
            if len(parts) >= 2 and parts[1].isdigit():
                n = max(n, int(parts[1]))
    return f"RULE-{n + 1:04d}"


def _slug(text: str) -> str:
    slug = "".join(c if c.isalnum() else "-" for c in text.lower())
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")[:40] or "rule"


def add_rule(root, scope, statement, rationale="", promoted_from="", approved_by=""):
    scope = scope.upper()
    if scope not in VALID_SCOPES:
        raise ValueError(f"scope must be one of {VALID_SCOPES}, got {scope!r}")
    if not statement.strip():
        raise ValueError("a rule needs a non-empty statement")
    directory = _rules_dir(root)
    directory.mkdir(parents=True, exist_ok=True)
    rule_id = _next_id(directory)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    fields = {
        "RULE_ID": rule_id,
        "SCOPE": scope,
        "STATUS": "APPROVED",
        "STATEMENT": statement,
    }
    if rationale:
        fields["RATIONALE"] = rationale
    if promoted_from:
        fields["PROMOTED_FROM"] = promoted_from
    if approved_by:
        fields["APPROVED_BY"] = approved_by
    fields["CREATED_AT"] = stamp
    lines = [f"{k} {v}".rstrip() for k, v in fields.items()]
    lines.append("END")
    path = directory / f"{rule_id}-{_slug(statement)}.pdl"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def load_rules(root):
    directory = _rules_dir(root)
    if not directory.is_dir():
        return []
    rules = []
    for p in sorted(directory.glob("*.pdl")):
        data = read_pdl(p)
        if data.get("STATUS", "APPROVED").upper() == "APPROVED":
            rules.append(data)
    order = {s: i for i, s in enumerate(VALID_SCOPES)}
    rules.sort(key=lambda d: (order.get(d.get("SCOPE", ""), 99), d.get("RULE_ID", "")))
    return rules


def list_rules(root) -> str:
    rules = load_rules(root)
    if not rules:
        return '(no rules recorded yet - add one with: pace rule add --scope PACE --statement "...")'
    out = []
    current = None
    for r in rules:
        scope = r.get("SCOPE", "")
        if scope != current:
            out.append(f"[{scope}]")
            current = scope
        out.append(f"  {r.get('RULE_ID','')}  {r.get('STATEMENT','')}")
    return "\n".join(out).strip()
