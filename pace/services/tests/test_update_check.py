"""Tests for the update-check service: notice only when newer, silence on
failure, sane version comparison. Run directly:
python pace/services/tests/test_update_check.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from pace.services.update_check import check_for_update, _parse, UPGRADE_COMMAND


def test_newer_version_produces_a_notice_with_the_command():
    info = check_for_update("0.2.0", fetch=lambda: "0.3.0")
    assert info is not None
    assert info["latest"] == "0.3.0" and info["current"] == "0.2.0"
    assert info["command"] == UPGRADE_COMMAND


def test_same_version_is_silent():
    assert check_for_update("0.2.0", fetch=lambda: "0.2.0") is None


def test_local_ahead_of_pypi_is_silent():
    assert check_for_update("0.3.0", fetch=lambda: "0.2.0") is None


def test_fetch_failure_is_silent():
    assert check_for_update("0.2.0", fetch=lambda: None) is None


def test_version_comparison_is_numeric_not_lexicographic():
    assert _parse("0.10.0") > _parse("0.9.0")
    assert check_for_update("0.9.0", fetch=lambda: "0.10.0") is not None


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"\n{len(tests)} tests passed")
