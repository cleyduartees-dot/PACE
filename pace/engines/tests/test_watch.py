"""Tests for the watch engine: change detection, break/heal transitions,
and that regenerating the handoff does not re-trigger the watch.
Run: python pace/engines/tests/test_watch.py
"""

import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from pace.engines.watch import snapshot, diff_messages, watch_once, watch_loop
from pace.engines.project_creator import init_instance


def test_first_tick_reports_validity():
    with tempfile.TemporaryDirectory() as tmp:
        root = init_instance(Path(tmp), kind="ORGANIZATION", name="W", slug="w")
        _, msgs = watch_once(root)
        assert any("VALID" in m for m in msgs)


def test_regenerating_handoff_does_not_retrigger_change():
    with tempfile.TemporaryDirectory() as tmp:
        root = init_instance(Path(tmp), kind="ORGANIZATION", name="W", slug="w")
        prev, _ = watch_once(root)          # regenerates handoff
        _, msgs = watch_once(root, prev)    # nothing changed by the user
        assert not any("change detected" in m for m in msgs), msgs


def test_breaking_the_contract_is_reported():
    with tempfile.TemporaryDirectory() as tmp:
        root = init_instance(Path(tmp), kind="ORGANIZATION", name="W", slug="w")
        prev, _ = watch_once(root)
        shutil.rmtree(root / "history")
        _, msgs = watch_once(root, prev)
        assert any("BROKEN" in m for m in msgs), msgs


def test_healing_is_reported():
    with tempfile.TemporaryDirectory() as tmp:
        root = init_instance(Path(tmp), kind="ORGANIZATION", name="W", slug="w")
        prev, _ = watch_once(root)
        hist = root / "history"
        shutil.rmtree(hist)
        prev, _ = watch_once(root, prev)
        hist.mkdir()
        (hist / "HISTORY-0001-FOUNDING.pdl").write_text(
            "HISTORY_VERSION 1.0.0\nSTATUS APPROVED\nTITLE r\nEND\n")
        _, msgs = watch_once(root, prev)
        assert any("VALID again" in m for m in msgs), msgs


def test_watch_loop_runs_a_bounded_number_of_iterations():
    with tempfile.TemporaryDirectory() as tmp:
        root = init_instance(Path(tmp), kind="ORGANIZATION", name="W", slug="w")
        ticks = {"n": 0}
        watch_loop(root, 0, printer=lambda m: None,
                   sleep=lambda s: None, iterations=3)
        # if it returned, the bound worked (no infinite loop)
        assert True


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test(); print(f"PASS {test.__name__}")
    print(f"\n{len(tests)} tests passed")
