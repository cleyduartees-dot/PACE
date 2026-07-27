"""Watch engine - the Active Guardian that floats: a dependency-free
polling loop that keeps an eye on a .pace/ instance and speaks only when
something changes (contract broke or healed, files changed, a newer engine
appeared). The continuous complement to per-message `pace check`.

Regenerable outputs (handoff/, memory/generated/) are excluded from the
change signature so regenerating the handoff never re-triggers the watch.
"""

import time
from pathlib import Path

from pace.kernel.kernel import validate_instance
from pace.engines.handoff import generate_handoff
from pace.services.update_check import latest_version_cached, _parse
from pace.services.version import PACE_VERSION

_IGNORED_TOP = {"handoff"}
_IGNORED_PAIR = {("memory", "generated")}


def _tree_mtime(root: Path) -> float:
    root = Path(root)
    latest = 0.0
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        parts = p.relative_to(root).parts
        if parts and parts[0] in _IGNORED_TOP:
            continue
        if len(parts) >= 2 and (parts[0], parts[1]) in _IGNORED_PAIR:
            continue
        try:
            latest = max(latest, p.stat().st_mtime)
        except OSError:
            pass
    return latest


def snapshot(root):
    violations = validate_instance(root)
    return {
        "valid": not violations,
        "violations": tuple(violations),
        "mtime": _tree_mtime(root),
        "latest": latest_version_cached(root),
    }


def diff_messages(old, new):
    msgs = []
    if old is None:
        msgs.append("contract VALID" if new["valid"]
                    else f"contract INVALID - {len(new['violations'])} violation(s)")
    else:
        if new["violations"] != old["violations"]:
            if new["valid"]:
                msgs.append("contract is VALID again")
            else:
                msgs.append(f"contract BROKEN - {len(new['violations'])} violation(s): "
                            + "; ".join(new["violations"]))
        if new["mtime"] > old["mtime"]:
            msgs.append("change detected in .pace/ - handoff refreshed")
    latest = new.get("latest")
    if latest and _parse(latest) > _parse(PACE_VERSION):
        if old is None or old.get("latest") != latest:
            msgs.append(f"a newer PACE engine ({latest}) is available - run `pace update`")
    return msgs


def watch_once(root, prev=None, regenerate=True):
    snap = snapshot(root)
    msgs = diff_messages(prev, snap)
    if regenerate and (prev is None or snap["mtime"] > prev["mtime"]):
        try:
            generate_handoff(root)
        except Exception:
            pass
    return snap, msgs


def watch_loop(root, interval, printer, sleep=time.sleep, iterations=None):
    prev = None
    count = 0
    while True:
        prev, msgs = watch_once(root, prev)
        for m in msgs:
            printer(m)
        count += 1
        if iterations is not None and count >= iterations:
            break
        sleep(interval)
    return prev
