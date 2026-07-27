"""Project Creator engine — init and create modes.

init_instance() attaches a valid, structurally minimal .pace/ instance to
a project directory that already exists (its own code lives elsewhere,
untouched).

create_project() generates a brand-new project from scratch: a fresh
directory, a git repository, a minimal README, and a .pace/ instance —
nothing stack-specific (no framework, no language scaffolding). That is
a separate, later capability (templates/, not yet built), not part of
this minimal create mode.
"""

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pace.services.contract_loader import load_instance_contract
from pace.services.version import PACE_VERSION

CONTRACT_PATH = Path(__file__).resolve().parent.parent / "contracts" / "INSTANCE_CONTRACT_0.2.0.pdl"
CONTRACT_VERSION = "0.2.0"

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
        "PACE_VERSION": PACE_VERSION,
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


def create_project(
    target_dir: Path,
    name: str,
    slug: str,
    org_ref: str,
    mission: str = PLACEHOLDER,
    vision: str = PLACEHOLDER,
    roadmap: str = PLACEHOLDER,
    sprint: str = PLACEHOLDER,
) -> Path:
    """Generate a brand-new project from scratch: creates `target_dir`
    (must not already exist or must be empty), initializes a git
    repository, writes a minimal README, and attaches a .pace/ instance.
    Stack-specific scaffolding is deliberately out of scope."""
    target_dir = Path(target_dir)
    if target_dir.exists() and any(target_dir.iterdir()):
        raise FileExistsError(f"{target_dir} already exists and is not empty")
    target_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        ["git", "init"], cwd=target_dir, check=True,
        capture_output=True, text=True,
    )

    (target_dir / "README.md").write_text(
        f"# {name}\n\nGoverned by PACE. See .pace/ for its mission, vision, roadmap and history.\n",
        encoding="utf-8",
    )

    return init_instance(
        target_dir, kind="PROJECT", name=name, slug=slug, org_ref=org_ref,
        mission=mission, vision=vision, roadmap=roadmap, sprint=sprint,
    )
