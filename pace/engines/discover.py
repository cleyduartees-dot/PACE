"""Discover engine - auto-read an existing project (README, code, git) and
PROPOSE a draft of what its .pace/ could say. It PROPOSES; the owner
(ROOT_AUTHORITY) confirms before anything becomes official (Governance
rule 1). Read-only: writes nothing. First path of the multi-source intake
(REQUEST-0011).
"""

import subprocess
from pathlib import Path

STACK_MARKERS = [
    ("package.json", "Node.js / JavaScript"),
    ("pyproject.toml", "Python"),
    ("requirements.txt", "Python"),
    ("go.mod", "Go"),
    ("Cargo.toml", "Rust"),
    ("pom.xml", "Java (Maven)"),
    ("build.gradle", "Java/Kotlin (Gradle)"),
    ("Gemfile", "Ruby"),
    ("composer.json", "PHP"),
    ("Dockerfile", "Docker"),
]

LANG_EXT = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".jsx": "React",
    ".tsx": "React/TS", ".go": "Go", ".rs": "Rust", ".java": "Java", ".rb": "Ruby",
    ".php": "PHP", ".c": "C", ".cpp": "C++", ".cs": "C#", ".html": "HTML",
    ".css": "CSS", ".md": "Markdown", ".sh": "Shell",
}

_SKIP = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "venv", ".pace", "_build_tmp"}


def _read_readme(root: Path):
    for name in ["README.md", "README.rst", "README.txt", "readme.md", "Readme.md"]:
        p = root / name
        if p.is_file():
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            meaningful = [l for l in lines if l.strip()][:8]
            return "\n".join(meaningful).strip() or None
    return None


def _detect_stack(root: Path):
    found = []
    for marker, label in STACK_MARKERS:
        if (root / marker).is_file() and label not in found:
            found.append(label)
    return found


def _top_languages(root: Path, limit=5):
    counts = {}
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in _SKIP for part in p.relative_to(root).parts):
            continue
        lang = LANG_EXT.get(p.suffix)
        if lang:
            counts[lang] = counts.get(lang, 0) + 1
    return sorted(counts.items(), key=lambda kv: -kv[1])[:limit]


def _git_recent(root: Path, n=5):
    if not (root / ".git").is_dir():
        return []
    try:
        out = subprocess.run(["git", "log", f"-{n}", "--pretty=%s"], cwd=str(root),
                             capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            return [l for l in out.stdout.splitlines() if l.strip()]
    except Exception:
        pass
    return []


def discover(root):
    root = Path(root)
    return {
        "name": root.resolve().name,
        "readme": _read_readme(root),
        "stack": _detect_stack(root),
        "languages": _top_languages(root),
        "recent_commits": _git_recent(root),
    }


def format_proposal(info) -> str:
    out = []
    out.append(f"PACE discovery - a PROPOSED draft for '{info['name']}'.")
    out.append("Nothing is written. This is a proposal for the owner to confirm.")
    out.append("Adopt with `pace init --guided` (or `pace init` then `pace supersede`).")
    out.append("")
    if info["stack"]:
        out.append("Detected stack: " + ", ".join(info["stack"]))
    if info["languages"]:
        out.append("Main languages: " + ", ".join(f"{k} ({v})" for k, v in info["languages"]))
    if not info["stack"] and not info["languages"]:
        out.append("No code stack detected - this may be a non-code project "
                   "(docs, an organization, a process). Consider `pace init --guided`.")
    if info["recent_commits"]:
        out.append("")
        out.append("Recent activity (git):")
        for c in info["recent_commits"]:
            out.append(f"  - {c}")
    out.append("")
    out.append("Proposed MISSION (draft - edit before adopting):")
    if info["readme"]:
        out.append("  (drawn from the README)")
        for line in info["readme"].splitlines()[:6]:
            out.append(f"  {line}")
    else:
        out.append(f"  {info['name']}: <why does this project exist? confirm with the owner>")
    return "\n".join(out)
