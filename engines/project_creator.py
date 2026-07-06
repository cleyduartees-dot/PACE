"""Project Creator engine — init mode only.

Attaches a valid, structurally minimal .pace/ instance to an existing
project directory. Generating a brand-new project from scratch
(pace create) is a separate, later capability of this same engine —
out of scope here.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from services.contract_loader import load_instance_contract

CONTRACT_PATH = Path(__file__).resolve().parent.parent / "contracts" / "INSTANCE_CONTRACT_0.1.0.pdl"
CONTRACT_VERSION = "0.1.0"

PLACEHOLDER = "Not yet defined."


def _write_pdl(path: Path, fields: dict) -> None:
    lines = [f"{key} {value}".rstrip() for key, value in fields.items()]
    lines.append("END")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def init_instance(
    target_dir: Path,
    kind: str,
    name: str,
    slug: str,
    org_ref: str = None,
    mission: str = PLACEHOLDER,
    vision: str = PLACEHOLDER,
    roadmap: str = PLACEHOLDER,
    sprint: str = PLACEHOLDER,
) -> Path:
    """Create a minimal, structurally valid .pace/ instance inside
    `target_dir`. Raises if one already exists there."""
    target_dir = Path(target_dir)
    root = target_dir / ".pace"
    if root.exists():
        raise FileExistsError(f".pace/ already exists at {root}")

    if kind == "PROJECT" and not org_ref:
        raise ValueError("KIND=PROJECT requires org_ref")

    contract = load_instance_contract(CONTRACT_PATH)

    for section in sorted(contract["sections"]):
        (root / section).mkdir(parents=True, exist_ok=True)

    created_at = datetime.now(timezone.utc).isoformat()

    instance_fields = {
        "KIND": kind,
        "NAME": name,
        "SLUG": slug,
        "SCHEMA_VERSION": CONTRACT_VERSION,
        "CREATED_AT": created_at,
    }
    if org_ref:
        instance_fields["ORG_REF"] = org_ref
    _write_pdl(root / "INSTANCE.pdl", instance_fields)

    _write_pdl(root / "mission" / "MISSION_1.0.0.pdl", {
        "MISSION_VERSION": "1.0.0", "STATUS": "APPROVED", "MISSION": mission,
    })
    _write_pdl(root / "vision" / "VISION_1.0.0.pdl", {
        "VISION_VERSION": "1.0.0", "STATUS": "APPROVED", "VISION": vision,
    })
    _write_pdl(root / "roadmap" / "ROADMAP_1.0.0.pdl", {
        "ROADMAP_VERSION": "1.0.0", "STATUS": "APPROVED", "ROADMAP": roadmap,
    })
    _write_pdl(root / "sprint" / "SPRINT_1.pdl", {
        "SPRINT_VERSION": "1", "STATUS": "ACTIVE", "SPRINT": sprint,
    })

    _write_pdl(root / "ACTIVE_VERSIONS.pdl", {
        "ACTIVE_MISSION": "mission/MISSION_1.0.0.pdl",
        "ACTIVE_VISION": "vision/VISION_1.0.0.pdl",
        "ACTIVE_ROADMAP": "roadmap/ROADMAP_1.0.0.pdl",
        "ACTIVE_SPRINT": "sprint/SPRINT_1.pdl",
    })

    _write_pdl(root / "history" / "HISTORY-0001-FOUNDING.pdl", {
        "HISTORY_VERSION": "1.0.0",
        "TYPE": "Founding",
        "STATUS": "APPROVED",
        "TITLE": f"{name} founded as a PACE-governed instance.",
    })

    return root
