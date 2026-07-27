"""Tests for the working-memory engine: remember/recall and condense
(archive old notes, keep recent, lose nothing, idempotent).
Run directly: python pace/engines/tests/test_memory.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from pace.engines.memory import remember, recall, condense


def test_remember_then_recall_roundtrips():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        remember(root, "first thing")
        remember(root, "second thing")
        text = recall(root)
        assert "first thing" in text and "second thing" in text


def test_recall_empty_is_friendly():
    with tempfile.TemporaryDirectory() as tmp:
        assert "no continuity memory" in recall(Path(tmp))


def test_condense_below_limit_is_a_noop():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for i in range(5):
            remember(root, f"n{i}")
        archived, _ = condense(root, keep=20)
        assert archived == 0


def test_condense_archives_old_keeps_recent_and_loses_nothing():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for i in range(1, 36):
            remember(root, f"note {i}")
        archived, archive = condense(root, keep=20)
        assert archived == 15
        work = (root / "memory/persistent/CONTINUITY.md").read_text()
        arch = archive.read_text()
        # oldest 15 archived, newest 20 kept
        assert "note 1" in arch and "note 15" in arch
        assert "note 16" in work and "note 35" in work
        # nothing lost: every note is somewhere
        for i in range(1, 36):
            assert (f"note {i}" in work) or (f"note {i}" in arch), i


def test_condense_is_idempotent():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for i in range(30):
            remember(root, f"x{i}")
        condense(root, keep=20)
        again, _ = condense(root, keep=20)
        assert again == 0


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"\n{len(tests)} tests passed")
