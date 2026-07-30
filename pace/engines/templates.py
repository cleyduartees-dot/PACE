"""Stack templates for pace create (templates/).

A template is a folder of starter files copied verbatim into a brand-new
project so it begins with a sensible stack skeleton. Templates are data,
not logic: PACE stays stdlib-only, and the copied files belong to the
user's project, never to PACE itself.
"""

import shutil
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def list_templates() -> list:
    if not TEMPLATES_DIR.is_dir():
        return []
    return sorted(p.name for p in TEMPLATES_DIR.iterdir() if p.is_dir())


def apply_template(target_dir, name) -> list:
    """Copy every file of template `name` into `target_dir`, preserving
    sub-paths. Returns the list of relative paths written. Raises
    ValueError for an unknown template."""
    src = TEMPLATES_DIR / name
    if not src.is_dir():
        raise ValueError(f"unknown template {name!r}; available: {list_templates()}")
    copied = []
    for item in sorted(src.rglob("*")):
        if item.is_file():
            rel = item.relative_to(src)
            dest = Path(target_dir) / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(item, dest)
            copied.append(str(rel))
    return copied
