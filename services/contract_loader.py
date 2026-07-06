"""Loads contracts/INSTANCE_CONTRACT_*.pdl at runtime, instead of the
Kernel hardcoding a hand transcription of its rules.

Purpose-built for the Instance Contract's known document shape, not a
fully general PDL engine — see protocols/PDL_SPECIFICATION_0.2.0.pdl.
"""

from pathlib import Path

from services.pdl_nested import split_top_level_sections, indented_field_names

TOP_LEVEL_SECTIONS = [
    "DEPENDS_ON", "PURPOSE", "ROOT_MANIFEST", "SECTIONS",
    "NOT_REPRESENTED_HERE", "HARD_RULES",
]

ROOT_MANIFEST_FILES = [".pace/INSTANCE.pdl", ".pace/ACTIVE_VERSIONS.pdl"]


def parse_root_manifest(root_manifest_text: str) -> dict:
    files = split_top_level_sections(root_manifest_text, ROOT_MANIFEST_FILES)
    return {
        name: indented_field_names(body, "REQUIRED_FIELDS", base_indent=4)
        for name, body in files.items()
    }


def parse_sections(sections_text: str) -> dict:
    """A SECTIONS entry header is a line at indentation 0, one or more
    comma-separated paths (e.g. 'mission/, vision/, roadmap/, sprint/'
    or a single 'history/'). Every section in Contract 0.1.0 requires
    its folder to exist, so this only needs to collect the paths."""
    sections = {}
    for line in sections_text.splitlines():
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent == 0:
            for raw_path in line.strip().split(","):
                path = raw_path.strip().rstrip("/")
                if path:
                    sections[path] = {"required": True}
    return sections


def load_instance_contract(path: Path) -> dict:
    text = Path(path).read_text(encoding="utf-8")
    first_line = text.splitlines()[0]
    contract_version = first_line.split(" ", 1)[1].strip() if " " in first_line else ""

    top = split_top_level_sections(text, TOP_LEVEL_SECTIONS)
    return {
        "contract_version": contract_version,
        "root_manifest": parse_root_manifest(top.get("ROOT_MANIFEST", "")),
        "sections": parse_sections(top.get("SECTIONS", "")),
    }
