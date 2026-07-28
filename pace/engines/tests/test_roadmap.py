"""Tests for the roadmap engine: parse items (item-level and phase-level
done), and drift detection vs a tracker export.
Run: python pace/engines/tests/test_roadmap.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from pace.engines.roadmap import parse_roadmap, drift
from pace.engines.project_creator import init_instance
from pace.cli.pace import main


def test_parse_marks_done_from_item_and_phase():
    with tempfile.TemporaryDirectory() as tmp:
        root = init_instance(Path(tmp), kind="ORGANIZATION", name="R", slug="r")
        content = ("intro line\n\nPHASE_1 X -- y   [DONE]\n  01  a\n  02  b\n\n"
                   "PHASE_2 Z -- w\n  03  c   [DONE, batched]\n  04  d")
        main(["supersede", "roadmap", content, str(Path(tmp))])
        items = {i["number"]: i for i in parse_roadmap(root)}
        assert items["01"]["done"] and items["02"]["done"], "phase-level done"
        assert items["03"]["done"] and not items["04"]["done"], "item-level done"


def test_drift_flags_missing_and_status_mismatch():
    items = [{"phase": "P", "number": "01", "title": "a [DONE]", "done": True},
             {"phase": "P", "number": "02", "title": "b", "done": False}]
    d = drift(items, [{"number": "01", "status": "to do"}])
    assert "02" in d["missing"]
    assert any(m["number"] == "01" for m in d["status_mismatch"])


def test_no_drift_when_in_sync():
    items = [{"phase": "P", "number": "01", "title": "a [DONE]", "done": True}]
    d = drift(items, [{"name": "F1 01 something", "status": "complete"}])
    assert not d["missing"] and not d["status_mismatch"]


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test(); print(f"PASS {test.__name__}")
    print(f"\n{len(tests)} tests passed")
