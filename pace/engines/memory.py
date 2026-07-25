"""Working-memory engine - the continuity notes an AI keeps so it does not
lose the thread within a long chat or across chats (the anti-"dementia"
layer). `remember` appends a note; `recall` prints the accumulated memory.

Lives in .pace/memory/persistent/CONTINUITY.md - refined in place, never
silently discarded (HAS_CONTINUITY_NOTE). Agreements that become permanent
graduate from here into decisions/ or history/; this file is the running
working memory, not the system of record.
"""

from datetime import datetime, timezone
from pathlib import Path

MEMORY_FILE = "memory/persistent/CONTINUITY.md"

_HEADER = (
    "# Continuity memory\n\n"
    "Running notes so an AI keeps the thread - objective, decisions, open\n"
    "threads, latest state. Newest last. Read this every turn; do not lose\n"
    "what was already agreed.\n\n"
)


def _memory_path(root: Path) -> Path:
    return Path(root) / MEMORY_FILE


def remember(root: Path, text: str) -> Path:
    path = _memory_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(_HEADER, encoding="utf-8")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"- [{stamp}] {text}\n")
    return path


def recall(root: Path) -> str:
    path = _memory_path(root)
    if not path.is_file():
        return '(no continuity memory yet - add notes with: pace remember "...")'
    return path.read_text(encoding="utf-8").strip()
