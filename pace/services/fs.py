"""Generic filesystem helpers shared by the Kernel and, later, Engines."""

from pathlib import Path


def find_upward(name: str, start: Path = None):
    """Walk upward from `start` (default: cwd) looking for a directory
    called `name` — the way Git locates `.git/` from anywhere inside a
    repository. Returns the matching Path, or None if not found."""
    current = Path(start or Path.cwd()).resolve()
    for directory in [current, *current.parents]:
        candidate = directory / name
        if candidate.is_dir():
            return candidate
    return None
