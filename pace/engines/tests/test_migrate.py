"""Tests for pace migrate (schema migration)."""
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from pace.engines.project_creator import init_instance
from pace.engines.migrate import migrate_instance


def _downgrade(root):
    inst = root / "INSTANCE.pdl"
    inst.write_text(inst.read_text(encoding="utf-8").replace("SCHEMA_VERSION 0.2.0", "SCHEMA_VERSION 0.1.0"), encoding="utf-8")
    if (root / "rules").exists():
        shutil.rmtree(root / "rules")


def test_migrate_01_to_02():
    with tempfile.TemporaryDirectory() as tmp:
        root = init_instance(Path(tmp), kind="PROJECT", name="X", slug="x", org_ref="org")
        _downgrade(root)
        frm, to, changes = migrate_instance(root)
        assert (frm, to) == ("0.1.0", "0.2.0")
        assert (root / "rules").is_dir()
        assert "SCHEMA_VERSION 0.2.0" in (root / "INSTANCE.pdl").read_text(encoding="utf-8")
        assert any("MIGRATION" in f.name for f in (root / "history").glob("*.pdl"))


def test_migrate_already_current_is_noop():
    with tempfile.TemporaryDirectory() as tmp:
        root = init_instance(Path(tmp), kind="PROJECT", name="X", slug="x", org_ref="org")
        assert migrate_instance(root) == ("0.2.0", "0.2.0", [])


def test_migrate_unknown_version_raises():
    with tempfile.TemporaryDirectory() as tmp:
        root = init_instance(Path(tmp), kind="PROJECT", name="X", slug="x", org_ref="org")
        inst = root / "INSTANCE.pdl"
        inst.write_text(inst.read_text(encoding="utf-8").replace("SCHEMA_VERSION 0.2.0", "SCHEMA_VERSION 9.9.9"), encoding="utf-8")
        try:
            migrate_instance(root)
            assert False, "should have raised"
        except ValueError:
            pass
