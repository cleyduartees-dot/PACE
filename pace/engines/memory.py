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


ARCHIVE_FILE = "memory/persistent/CONTINUITY_ARCHIVE.md"

_ARCHIVE_HEADER = (
    "# Continuity archive\n\n"
    "Older continuity notes moved out of the working log to keep it lean.\n"
    "Nothing is discarded - this is the full history, oldest first.\n\n"
)


def _archive_path(root: Path) -> Path:
    return Path(root) / ARCHIVE_FILE


def condense(root: Path, keep: int = 20):
    """Keep the most recent `keep` real notes in the working log and move
    the older ones to CONTINUITY_ARCHIVE.md. Refines in place without
    discarding: the archive holds the full history. Condensation markers
    are ephemeral pointers - never counted nor archived - so running this
    again with nothing new to move is a no-op. Returns
    (archived_count, archive_path)."""
    path = _memory_path(root)
    if not path.is_file():
        return (0, _archive_path(root))
    all_lines = [l for l in path.read_text(encoding="utf-8").splitlines()
                 if l.strip().startswith("- ")]
    real = [n for n in all_lines if "(condensed)" not in n]
    if len(real) <= keep:
        return (0, _archive_path(root))
    old, recent = real[:-keep], real[-keep:]

    archive = _archive_path(root)
    archive.parent.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        archive.write_text(_ARCHIVE_HEADER, encoding="utf-8")
    with archive.open("a", encoding="utf-8") as handle:
        for line in old:
            handle.write(line + "\n")

    total_archived = sum(1 for l in archive.read_text(encoding="utf-8").splitlines()
                         if l.strip().startswith("- "))
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    marker = (f"- [{stamp}] (condensed) {total_archived} earlier note(s) live in "
              "CONTINUITY_ARCHIVE.md; nothing discarded.")
    path.write_text(_HEADER + marker + "\n" + "\n".join(recent) + "\n", encoding="utf-8")
    return (len(old), archive)
