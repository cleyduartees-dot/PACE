"""Proves init_instance() produces something the Kernel considers
structurally valid — not just that it writes files. Run directly:
python engines/tests/test_project_creator.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from engines.project_creator import init_instance
from kernel.kernel import locate_instance, validate_instance


def test_init_produces_a_structurally_valid_instance():
    with tempfile.TemporaryDirectory() as tmp:
        root = init_instance(
            Path(tmp), kind="PROJECT", name="Test Project",
            slug="test-project", org_ref="test-org",
        )
        assert root == Path(tmp) / ".pace"
        assert locate_instance(Path(tmp)) == root
        violations = validate_instance(root)
        assert violations == [], violations


def test_init_refuses_to_overwrite_an_existing_instance():
    with tempfile.TemporaryDirectory() as tmp:
        init_instance(Path(tmp), kind="PROJECT", name="X", slug="x", org_ref="org")
        try:
            init_instance(Path(tmp), kind="PROJECT", name="X", slug="x", org_ref="org")
            assert False, "expected FileExistsError"
        except FileExistsError:
            pass


def test_init_requires_org_ref_for_project_kind():
    with tempfile.TemporaryDirectory() as tmp:
        try:
            init_instance(Path(tmp), kind="PROJECT", name="X", slug="x")
            assert False, "expected ValueError"
        except ValueError:
            pass


def test_init_organization_kind_does_not_require_org_ref():
    with tempfile.TemporaryDirectory() as tmp:
        root = init_instance(Path(tmp), kind="ORGANIZATION", name="Org", slug="org")
        violations = validate_instance(root)
        assert violations == [], violations


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"\n{len(tests)} tests passed")
