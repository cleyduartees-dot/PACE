"""Nested-section extraction for PDL documents that mix structural
fields with hand-wrapped prose (governance/ontology/contracts documents),
on top of pdl.py's flat grammar.

See protocols/PDL_SPECIFICATION_0.2.0.pdl for why this deliberately does
not auto-detect section headers: a document that uses indentation both
for structure and for visual line-wrap alignment cannot be told apart
generically without guessing. Instead, the caller supplies the small,
fixed vocabulary of top-level section names it expects — the same
technique the old system's BOOTSTRAP_CONTEXT.pdl already used via its
own READ_ORDER list.
"""


def split_top_level_sections(text: str, known_sections) -> dict:
    """Split a document into named top-level blocks. A line is treated
    as the start of a new section only if, once stripped, it exactly
    matches one of `known_sections`. Everything up to the next known
    section name (or END) becomes that section's raw body text."""
    known = set(known_sections)
    sections = {}
    current_name = None
    current_lines = []

    def flush():
        if current_name is not None:
            sections[current_name] = "\n".join(current_lines).strip("\n")

    for line in text.splitlines():
        stripped = line.strip()
        if stripped in known:
            flush()
            current_name = stripped
            current_lines = []
        elif stripped == "END":
            break
        elif current_name is not None:
            current_lines.append(line)
    flush()
    return sections


def indented_field_names(text: str, header: str, base_indent: int) -> list:
    """Within `text`, find the block introduced by a line equal to
    `header`, then collect the first token of every subsequent line
    indented at exactly `base_indent`. Lines indented deeper than
    `base_indent` are continuations of the previous field's wrapped
    value, not new fields, and are ignored here."""
    names = []
    in_block = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        indent = len(line) - len(line.lstrip(" "))
        if not in_block:
            if stripped == header:
                in_block = True
            continue
        if indent < base_indent:
            break
        if indent == base_indent:
            names.append(stripped.split()[0])
    return names
