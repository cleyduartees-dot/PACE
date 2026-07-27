"""Tests for the cached version lookup used by `pace check`."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from pace.services.update_check import latest_version_cached


def test_cache_avoids_a_second_fetch_within_ttl():
    calls = {"n": 0}
    def fetch():
        calls["n"] += 1
        return "9.9.9"
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "memory" / "generated").mkdir(parents=True)
        a = latest_version_cached(tmp, ttl_seconds=3600, fetch=fetch)
        b = latest_version_cached(tmp, ttl_seconds=3600, fetch=fetch)
        assert a == "9.9.9" and b == "9.9.9"
        assert calls["n"] == 1, calls


def test_zero_ttl_forces_a_refetch():
    calls = {"n": 0}
    def fetch():
        calls["n"] += 1
        return "1.0.0"
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "memory" / "generated").mkdir(parents=True)
        latest_version_cached(tmp, ttl_seconds=0, fetch=fetch)
        latest_version_cached(tmp, ttl_seconds=0, fetch=fetch)
        assert calls["n"] == 2, calls


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test(); print(f"PASS {test.__name__}")
    print(f"\n{len(tests)} tests passed")
