"""PACE Kernel — locates a .pace/ instance and validates it structurally
against contracts/INSTANCE_CONTRACT_0.1.0.pdl, loaded at runtime from the
actual file, not a hand transcription of its rules.

Deliberately minimal: this is structural validation only (does the
required shape exist, is SCHEMA_VERSION supported). Deeper, semantic
validation belongs to the future Doctor engine, not the Kernel.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from services.fs import find_upward
from services.pdl import read_pdl
from services.contract_loader import load_instance_contract
from services.validate import (
    require_fields,
    require_dirs,
    require_non_empty_dir,
    forbid_file_suffixes,
)

CONTRACT_PATH = Path(__file__).resolve().parent.parent / "contracts" / "INSTANCE_CONTRACT_0.1.0.pdl"

# Which contract versions THIS Kernel build understands — a property of
# the installed engine, not something the contract document itself can
# declare (a v0.1 contract cannot know what future kernels will support).
SUPPORTED_SCHEMA_VERSIONS = {"0.1.0"}

# HARD_RULE 2 ("no code, script or executable file") is prose, not a
# machine-enumerable list — this is the Kernel's own codified reading of
# that rule, not something extracted from the contract text.
FORBIDDEN_SUFFIXES = {".py", ".ts", ".js", ".sh", ".exe", ".ps1", ".bat"}


def locate_instance(start: Path = None):
    """Find the nearest .pace/ directory walking upward from `start`."""
    return find_upward(".pace", start)


def validate_instance(root: Path) -> list:
    """Structural validation only. Returns a list of violations; an
    empty list means the instance is structurally valid."""
    violations = []
    contract = load_instance_contract(CONTRACT_PATH)

    instance_file = root / "INSTANCE.pdl"
    if not instance_file.is_file():
        violations.append("missing INSTANCE.pdl")
    else:
        instance = read_pdl(instance_file)
        required = contract["root_manifest"].get(".pace/INSTANCE.pdl", [])
        violations += require_fields(instance, required, "INSTANCE.pdl")
        if instance.get("KIND") == "PROJECT" and not instance.get("ORG_REF"):
            violations.append("INSTANCE.pdl KIND=PROJECT requires ORG_REF")
        schema_version = instance.get("SCHEMA_VERSION")
        if schema_version and schema_version not in SUPPORTED_SCHEMA_VERSIONS:
            violations.append(
                f"SCHEMA_VERSION {schema_version} not supported by this "
                f"Kernel (supports {sorted(SUPPORTED_SCHEMA_VERSIONS)}) — "
                "needs pace migrate, not yet built"
            )

    active_versions_file = root / "ACTIVE_VERSIONS.pdl"
    if not active_versions_file.is_file():
        violations.append("missing ACTIVE_VERSIONS.pdl")
    else:
        active_versions = read_pdl(active_versions_file)
        required = contract["root_manifest"].get(".pace/ACTIVE_VERSIONS.pdl", [])
        violations += require_fields(active_versions, required, "ACTIVE_VERSIONS.pdl")

    violations += require_dirs(root, sorted(contract["sections"]))
    violations += require_non_empty_dir(root, "history")
    violations += forbid_file_suffixes(root, FORBIDDEN_SUFFIXES)

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
