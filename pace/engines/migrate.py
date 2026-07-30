"""PACE schema migration (pace migrate).

Brings a .pace/ instance from an older Contract SCHEMA_VERSION up to the
one this engine writes. Migrations are additive and conservative: they
never delete content. Each migration is a small, explicit step; today the
only one is 0.1.0 -> 0.2.0 (which introduced the optional rules/ section).
"""

from datetime import datetime, timezone
from pathlib import Path

from pace.services.pdl import read_pdl
from pace.services.version import PACE_VERSION
from pace.engines.project_creator import CONTRACT_VERSION

# Ordered chain of schema versions this engine knows how to move through.
_CHAIN = ["0.1.0", "0.2.0"]


def _set_field(text: str, key: str, value: str) -> str:
    out = []
    for line in text.splitlines():
        if line.startswith(key + " "):
            out.append(f"{key} {value}")
        else:
            out.append(line)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def migrate_instance(root: Path):
    """Migrate the instance at `root` up to CONTRACT_VERSION. Returns
    (from_version, to_version, changes). Raises ValueError when the
    instance declares a version this engine cannot migrate."""
    root = Path(root)
    instance_file = root / "INSTANCE.pdl"
    if not instance_file.is_file():
        raise ValueError("no INSTANCE.pdl found; not a .pace/ instance")
    current = read_pdl(instance_file).get("SCHEMA_VERSION", "")
    target = CONTRACT_VERSION

    if current == target:
        return (current, target, [])
    if current not in _CHAIN:
        raise ValueError(
            f"SCHEMA_VERSION {current!r} is not one this engine can migrate "
            f"(knows: {_CHAIN}); this engine may be behind - update pace"
        )
    if _CHAIN.index(current) > _CHAIN.index(target):
        raise ValueError(
            f"instance is at {current}, newer than this engine's {target}; "
            "update pace instead of migrating down"
        )

    changes = []
    for step_from, step_to in zip(_CHAIN, _CHAIN[1:]):
        if _CHAIN.index(step_from) < _CHAIN.index(current):
            continue
        if _CHAIN.index(step_to) > _CHAIN.index(target):
            break
        if step_from == "0.1.0" and step_to == "0.2.0":
            rules_dir = root / "rules"
            if not rules_dir.exists():
                rules_dir.mkdir(parents=True, exist_ok=True)
                changes.append("created the optional rules/ section")

    text = instance_file.read_text(encoding="utf-8")
    text = _set_field(text, "SCHEMA_VERSION", target)
    text = _set_field(text, "PACE_VERSION", PACE_VERSION)
    instance_file.write_text(text, encoding="utf-8")
    changes.append(f"SCHEMA_VERSION {current} -> {target}")

    hist_dir = root / "history"
    hist_dir.mkdir(parents=True, exist_ok=True)
    n = len(list(hist_dir.glob("HISTORY-*.pdl"))) + 1
    stamp = datetime.now(timezone.utc).isoformat()
    (hist_dir / f"HISTORY-{n:04d}-MIGRATION.pdl").write_text(
        "HISTORY_VERSION 1.0.0\nTYPE Migration\nSTATUS APPROVED\n"
        f"TITLE Migrated schema {current} -> {target}.\nAT {stamp}\nEND\n",
        encoding="utf-8",
    )
    return (current, target, changes)
