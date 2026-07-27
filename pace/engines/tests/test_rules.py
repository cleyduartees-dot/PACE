"""Tests for the rules engine: correlative IDs, scope validation, load
ordering, and that an instance with a rules/ folder stays structurally
valid. Run directly: python pace/engines/tests/test_rules.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from pace.engines.rules import add_rule, load_rules, list_rules, VALID_SCOPES
from pace.engines.project_creator import init_instance
from pace.kernel.kernel import validate_instance


def test_add_rule_assigns_sequential_ids():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        a = add_rule(root, "PACE", "First rule.")
        b = add_rule(root, "PACE", "Second rule.")
        assert a.name.startswith("RULE-0001")
        assert b.name.startswith("RULE-0002")


def test_invalid_scope_is_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        try:
            add_rule(Path(tmp), "TEAM", "nope")
            assert False, "expected ValueError"
        except ValueError:
            pass


def test_empty_statement_is_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        try:
            add_rule(Path(tmp), "PACE", "   ")
            assert False, "expected ValueError"
        except ValueError:
            pass


def test_load_rules_orders_by_scope_then_id():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        add_rule(root, "PROJECT", "p rule")
        add_rule(root, "PACE", "pace rule")
        add_rule(root, "ORGANIZATION", "org rule")
        scopes = [r["SCOPE"] for r in load_rules(root)]
        assert scopes == ["PACE", "ORGANIZATION", "PROJECT"], scopes


def test_load_rules_on_missing_dir_is_empty():
    with tempfile.TemporaryDirectory() as tmp:
        assert load_rules(Path(tmp)) == []
        assert "no rules recorded" in list_rules(Path(tmp))


def test_instance_with_rules_folder_is_valid():
    with tempfile.TemporaryDirectory() as tmp:
        root = init_instance(Path(tmp), kind="ORGANIZATION", name="X", slug="x")
        add_rule(root, "PACE", "some rule")
        assert validate_instance(root) == []


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"\n{len(tests)} tests passed")
