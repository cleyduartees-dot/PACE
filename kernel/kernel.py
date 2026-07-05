"""PACE Kernel — locates a .pace/ instance and validates it structurally
against contracts/INSTANCE_CONTRACT_0.1.0.pdl.

Deliberately minimal: this is structural validation only (does the
required shape exist, is SCHEMA_VERSION supported). Deeper, semantic
validation belongs to the future Doctor engine, not the Kernel.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from services.fs import find_upward
from services.pdl import read_pdl

SUPPORTED_SCHEMA_VERSIONS = {"0.1.0"}

REQUIRED_SECTIONS = [
    "mission", "vision", "roadmap", "sprint", "handoff",
    "history", "releases", "decisions", "requests",
    "memory/generated", "memory/persistent",
]

FORBIDDEN_SUFFIXES = {".py", ".ts", ".js", ".sh", ".exe", ".ps1", ".bat"}


def locate_instance(start: Path = None):
    """Find the nearest .pace/ directory walking upward from `start`."""
    return find_upward(".pace", start)


def validate_instance(root: Path) -> list:
    """Structural validation only. Returns a list of violations; an
    empty list means the instance is structurally valid."""
    violations = []

    instance_file = root / "INSTANCE.pdl"
    active_versions_file = root / "ACTIVE_VERSIONS.pdl"

    if not instance_file.is_file():
        violations.append("missing INSTANCE.pdl")
    else:
        instance = read_pdl(instance_file)
        for field in ("KIND", "NAME", "SLUG", "SCHEMA_VERSION", "CREATED_AT"):
            if not instance.get(field):
                violations.append(f"INSTANCE.pdl missing required field {field}")
        if instance.get("KIND") == "PROJECT" and not instance.get("ORG_REF"):
            violations.append("INSTANCE.pdl KIND=PROJECT requires ORG_REF")
        schema_version = instance.get("SCHEMA_VERSION")
        if schema_version and schema_version not in SUPPORTED_SCHEMA_VERSIONS:
            violations.append(
                f"SCHEMA_VERSION {schema_version} not supported by this "
                f"Kernel (supports {sorted(SUPPORTED_SCHEMA_VERSIONS)}) — "
                "needs pace migrate, not yet built"
            )

    if not active_versions_file.is_file():
        violations.append("missing ACTIVE_VERSIONS.pdl")
    else:
        active_versions = read_pdl(active_versions_file)
        for field in ("ACTIVE_MISSION", "ACTIVE_VISION", "ACTIVE_ROADMAP", "ACTIVE_SPRINT"):
            if not active_versions.get(field):
                violations.append(f"ACTIVE_VERSIONS.pdl missing required field {field}")

    for section in REQUIRED_SECTIONS:
        if not (root / section).is_dir():
            violations.append(f"missing required section {section}/")

    history_dir = root / "history"
    if history_dir.is_dir() and not any(history_dir.iterdir()):
        violations.append("history/ exists but has no founding entry")

    for path in root.rglob("*"):
        if path.is_file() and path.suffix in FORBIDDEN_SUFFIXES:
            violations.append(f"forbidden code/script file inside .pace/: {path.relative_to(root)}")

    return violations


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    root = locate_instance(target)
    if root is None:
        print("no .pace/ instance found")
        raise SystemExit(1)
    print(f"instance located at {root}")
    violations = validate_instance(root)
    if violations:
        print(f"INVALID — {len(violations)} violation(s):")
        for v in violations:
            print(f"  - {v}")
        raise SystemExit(1)
    print("VALID")
