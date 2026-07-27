"""Update-check service - the Active Guardian telling its user when a
newer PACE engine exists, with the exact command to run, so nobody has
to go check PyPI by hand (REQUEST-0012).

Fail-silent by design: offline, slow network, or an unexpected PyPI
response all mean "no notice", never an error or a hang - the check uses
a short timeout and swallows every exception.
"""

import json
from urllib.request import urlopen

PYPI_URL = "https://pypi.org/pypi/pace-engine/json"
UPGRADE_COMMAND = "pace update  (or: pip install --upgrade pace-engine)"


def _parse(version: str) -> tuple:
    parts = []
    for piece in str(version).split("."):
        digits = "".join(ch for ch in piece if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def latest_version(timeout: float = 2.0):
    """Latest pace-engine version on PyPI, or None if unreachable."""
    try:
        with urlopen(PYPI_URL, timeout=timeout) as response:
            return json.load(response)["info"]["version"]
    except Exception:
        return None


def check_for_update(current: str, fetch=latest_version):
    """Return {'current', 'latest', 'command'} when a newer version
    exists, else None. `fetch` is injectable for tests."""
    latest = fetch()
    if not latest:
        return None
    if _parse(latest) > _parse(current):
        return {"current": current, "latest": latest, "command": UPGRADE_COMMAND}
    return None
