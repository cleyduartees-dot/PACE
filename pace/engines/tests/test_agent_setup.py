"""Tests for per-message enforcement wiring: the Claude Code hook, Cursor
rule, and their idempotency / non-clobbering.
Run: python pace/engines/tests/test_agent_setup.py
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from pace.engines.agent_setup import install_claude_hook, install_cursor_rule, CHECK_COMMAND
from pace.engines.project_creator import init_instance


def _inst(tmp):
    return init_instance(Path(tmp), kind="ORGANIZATION", name="X", slug="x")


def test_claude_hook_written_with_the_check_command():
    with tempfile.TemporaryDirectory() as tmp:
        root = _inst(tmp)
        path, created = install_claude_hook(root)
        assert created
        data = json.loads(path.read_text())
        cmds = [h["command"] for g in data["hooks"]["UserPromptSubmit"] for h in g["hooks"]]
        assert CHECK_COMMAND in cmds


def test_claude_hook_is_idempotent_and_preserves_other_settings():
    with tempfile.TemporaryDirectory() as tmp:
        root = _inst(tmp)
        path, _ = install_claude_hook(root)
        data = json.loads(path.read_text()); data["model"] = "sonnet"
        path.write_text(json.dumps(data))
        path2, created = install_claude_hook(root)
        assert not created
        d2 = json.loads(path2.read_text())
        assert d2["model"] == "sonnet"
        assert len(d2["hooks"]["UserPromptSubmit"]) == 1


def test_claude_hook_does_not_clobber_a_foreign_hook():
    with tempfile.TemporaryDirectory() as tmp:
        root = _inst(tmp)
        settings = Path(tmp) / ".claude" / "settings.json"
        settings.parent.mkdir(parents=True, exist_ok=True)
        settings.write_text(json.dumps({"hooks": {"UserPromptSubmit": [
            {"hooks": [{"type": "command", "command": "echo other"}]}]}}))
        path, _ = install_claude_hook(root)
        cmds = [h["command"] for g in json.loads(path.read_text())["hooks"]["UserPromptSubmit"] for h in g["hooks"]]
        assert "echo other" in cmds and CHECK_COMMAND in cmds


def test_cursor_rule_is_always_applied():
    with tempfile.TemporaryDirectory() as tmp:
        root = _inst(tmp)
        path, created = install_cursor_rule(root)
        assert created and path.name == "pace.mdc"
        assert "alwaysApply: true" in path.read_text() and "pace check" in path.read_text()


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test(); print(f"PASS {test.__name__}")
    print(f"\n{len(tests)} tests passed")
