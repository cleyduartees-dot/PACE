"""Tests for the hooks engine and the AGENTS.md auto-pointer.
Run directly: python pace/engines/tests/test_hooks.py
"""

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from pace.engines.hooks import install_hook, uninstall_hook, MARKER
from pace.engines.handoff import generate_handoff, _ensure_agents_pointer
from pace.engines.project_creator import init_instance


def _git_project(tmp):
    target = Path(tmp)
    subprocess.run(["git", "init", "-q"], cwd=target, check=True)
    root = init_instance(target, kind="ORGANIZATION", name="H", slug="h")
    return root


def test_install_writes_an_executable_marked_hook():
    with tempfile.TemporaryDirectory() as tmp:
        root = _git_project(tmp)
        hook = install_hook(root)
        text = hook.read_text()
        assert MARKER in text and "pace doctor" in text.replace("pace.cli.pace", "")
        assert hook.stat().st_mode & 0o111


def test_install_is_idempotent():
    with tempfile.TemporaryDirectory() as tmp:
        root = _git_project(tmp)
        first = install_hook(root).read_text()
        second = install_hook(root).read_text()
        assert first == second


def test_install_refuses_a_foreign_hook():
    with tempfile.TemporaryDirectory() as tmp:
        root = _git_project(tmp)
        hooks = Path(tmp) / ".git" / "hooks"
        hooks.mkdir(parents=True, exist_ok=True)
        (hooks / "pre-commit").write_text("#!/bin/sh\nsomeone else's hook\n")
        try:
            install_hook(root)
            assert False, "expected FileExistsError"
        except FileExistsError:
            pass


def test_install_without_git_repo_raises():
    with tempfile.TemporaryDirectory() as tmp:
        root = init_instance(Path(tmp), kind="ORGANIZATION", name="X", slug="x")
        try:
            install_hook(root)
            assert False, "expected FileNotFoundError"
        except FileNotFoundError:
            pass


def test_uninstall_neutralizes_our_hook():
    with tempfile.TemporaryDirectory() as tmp:
        root = _git_project(tmp)
        install_hook(root)
        hook = uninstall_hook(root)
        assert "exit 0" in hook.read_text()


def test_handoff_creates_agents_pointer_only_when_absent():
    with tempfile.TemporaryDirectory() as tmp:
        root = init_instance(Path(tmp), kind="ORGANIZATION", name="A", slug="a")
        generate_handoff(root)
        agents = Path(tmp) / "AGENTS.md"
        assert agents.is_file() and "pace handoff" in agents.read_text()
        agents.write_text("OWNER CONTENT")
        generate_handoff(root)
        assert agents.read_text() == "OWNER CONTENT"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"\n{len(tests)} tests passed")
