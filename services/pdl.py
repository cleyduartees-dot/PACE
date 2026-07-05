"""Minimal PDL parser for flat key-value documents.

Implements the grammar in protocols/PDL_SPECIFICATION_0.1.0.pdl: one
KEY VALUE pair per line, blank lines ignored, terminated by END.
"""

from pathlib import Path


def parse_pdl(text: str) -> dict:
    fields = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line == "END":
            break
        if " " in line:
            key, value = line.split(" ", 1)
        else:
            key, value = line, ""
        fields[key] = value.strip()
    return fields


def read_pdl(path: Path) -> dict:
    return parse_pdl(Path(path).read_text(encoding="utf-8"))
