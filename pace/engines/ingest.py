"""Ingest engine - read documents a client provides (README, notes, specs,
PDFs) and PROPOSE what PACE deduced: the themes, the headings, a context
draft. It PROPOSES; the owner confirms before anything becomes official
(Governance rule 1). Read-only. Second path of the multi-source intake
(REQUEST-0011).

Text documents (.md/.txt/.rst) are read with zero dependencies. PDFs are
extracted only if an optional extractor (pypdf) is installed - absent, they
are skipped with a note, never an error. PACE keeps no required deps.
"""

import re
from pathlib import Path

TEXT_EXT = {".md", ".markdown", ".txt", ".rst"}
_SKIP = {".git", "node_modules", ".pace", "__pycache__", ".venv", "venv", "dist", "build", "_build_tmp"}

_STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "is", "are", "on",
    "with", "that", "this", "it", "as", "by", "at", "be", "from", "will", "can",
    "not", "but", "you", "your", "was", "has", "have", "its", "which", "into",
    "de", "la", "el", "los", "las", "un", "una", "unos", "unas", "y", "o", "en",
    "que", "para", "con", "por", "se", "del", "al", "es", "su", "sus", "lo", "como",
}


def _keywords(text, n=10):
    counts = {}
    for w in re.findall(r"[a-zA-ZÀ-ſ]{4,}", text.lower()):
        if w in _STOP:
            continue
        counts[w] = counts.get(w, 0) + 1
    return sorted(counts.items(), key=lambda kv: -kv[1])[:n]


def _headings(text):
    return [l.strip("# ").strip() for l in text.splitlines()
            if l.strip().startswith("#") and len(l.strip()) > 1][:5]


def _extract_pdf(path):
    try:
        import pypdf
        reader = pypdf.PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:
        return None


def _collect(path):
    path = Path(path)
    files = [path] if path.is_file() else [p for p in path.rglob("*") if p.is_file()]
    docs, skipped_pdfs = [], 0
    for p in files:
        if any(part in _SKIP for part in p.parts):
            continue
        suffix = p.suffix.lower()
        if suffix in TEXT_EXT:
            try:
                docs.append((p.name, p.read_text(encoding="utf-8", errors="replace")))
            except OSError:
                pass
        elif suffix == ".pdf":
            text = _extract_pdf(p)
            if text:
                docs.append((p.name, text))
            else:
                skipped_pdfs += 1
    return docs, skipped_pdfs


def ingest(path):
    docs, skipped_pdfs = _collect(path)
    combined = "\n".join(t for _, t in docs)
    headings = []
    for _, t in docs:
        headings.extend(_headings(t))
    return {
        "path": str(path),
        "documents": [n for n, _ in docs],
        "headings": headings[:12],
        "keywords": _keywords(combined),
        "chars": len(combined),
        "skipped_pdfs": skipped_pdfs,
    }


def format_proposal(info) -> str:
    out = []
    out.append(f"PACE ingestion - a PROPOSED reading of documents under '{info['path']}'.")
    out.append("Nothing is written. Confirm with the owner, then adopt into the")
    out.append("relevant section with `pace supersede` or `pace init --guided`.")
    out.append("")
    if not info["documents"]:
        out.append("No text documents found (.md/.txt/.rst).")
        if info["skipped_pdfs"]:
            out.append(f"{info['skipped_pdfs']} PDF(s) skipped - install `pypdf` to include them.")
        return "\n".join(out)
    out.append(f"Documents read ({len(info['documents'])}): " + ", ".join(info["documents"][:12]))
    if info["skipped_pdfs"]:
        out.append(f"({info['skipped_pdfs']} PDF(s) skipped - install `pypdf` to include them.)")
    if info["keywords"]:
        out.append("")
        out.append("Main themes (deduced): " + ", ".join(f"{k} ({v})" for k, v in info["keywords"]))
    if info["headings"]:
        out.append("")
        out.append("Section headings found:")
        for h in info["headings"]:
            out.append(f"  - {h}")
    out.append("")
    out.append("Proposed CONTEXT draft: the project appears to be about "
               + (", ".join(k for k, _ in info["keywords"][:5]) or "<unclear>")
               + ". Confirm the mission and scope with the owner before adopting.")
    return "\n".join(out)
