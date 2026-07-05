"""Smoke test for the Kernel. Run directly: python kernel/tests/test_kernel.py"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from kernel.kernel import locate_instance, validate_instance

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "example_instance"


def test_locate_finds_pace_from_inside_the_fixture():
    root = locate_instance(FIXTURE)
    assert root == FIXTURE / ".pace", root


def test_locate_finds_pace_from_a_nested_subdirectory():
    root = locate_instance(FIXTURE / ".pace" / "mission")
    assert root == FIXTURE / ".pace", root


def test_valid_fixture_has_no_violations():
    violations = validate_instance(FIXTURE / ".pace")
    assert violations == [], violations


def test_missing_instance_file_is_a_violation():
    with tempfile.TemporaryDirectory() as tmp:
        broken = Path(tmp) / ".pace"
        broken.mkdir()
        violations = validate_instance(broken)
        assert "missing INSTANCE.pdl" in violations


def test_unsupported_schema_version_is_a_violation():
    with tempfile.TemporaryDirectory() as tmp:
        broken = Path(tmp) / ".pace"
        broken.mkdir()
        (broken / "INSTANCE.pdl").write_text(
            "KIND PROJECT\nNAME X\nSLUG x\nSCHEMA_VERSION 9.9.9\n"
            "ORG_REF x\nCREATED_AT now\nEND\n"
        )
        violations = validate_instance(broken)
        assert any("SCHEMA_VERSION 9.9.9 not supported" in v for v in violations), violations


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"\n{len(tests)} tests passed")
