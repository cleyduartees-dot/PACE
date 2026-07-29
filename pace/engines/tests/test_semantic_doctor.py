"""Tests for the semantic Doctor (pace doctor --deep)."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from pace.engines.project_creator import init_instance
from pace.engines.semantic_doctor import semantic_check


def test_fresh_project_flags_placeholders_and_no_authority():
    with tempfile.TemporaryDirectory() as tmp:
        root = init_instance(Path(tmp), kind="PROJECT", name="X", slug="x", org_ref="org")
        joined = " ".join(semantic_check(root))
        assert "mission is still a placeholder" in joined
        assert "ROOT_AUTHORITY" in joined


def test_fully_seeded_project_is_clean():
    with tempfile.TemporaryDirectory() as tmp:
        root = init_instance(
            Path(tmp), kind="PROJECT", name="X", slug="x", org_ref="org",
            mission="Real mission", vision="Real vision", roadmap="01 do it",
            owner="Ada Lovelace", owner_role="Founder",
        )
        assert semantic_check(root) == []


def test_dangling_active_pointer_detected():
    with tempfile.TemporaryDirectory() as tmp:
        root = init_instance(
            Path(tmp), kind="PROJECT", name="X", slug="x", org_ref="org",
            mission="m", vision="v", roadmap="r", owner="Ada", owner_role="F",
        )
        av = root / "ACTIVE_VERSIONS.pdl"
        av.write_text(
            av.read_text(encoding="utf-8").replace("roadmap/ROADMAP_1.0.0.pdl", "roadmap/GONE.pdl"),
            encoding="utf-8",
        )
        assert any("ACTIVE_ROADMAP points to a missing file" in i for i in semantic_check(root))
