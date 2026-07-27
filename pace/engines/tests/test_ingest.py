"""Tests for the ingest engine: reads text docs, deduces themes/headings,
proposes, writes nothing. Run: python pace/engines/tests/test_ingest.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from pace.engines.ingest import ingest, format_proposal


def _docs(tmp):
    root = Path(tmp)
    (root / "spec.md").write_text("# Payments Spec\n\nInvoices, invoices, billing and refunds.\n")
    (root / "notes.txt").write_text("The billing system handles invoices and refunds daily.\n")
    return root


def test_reads_text_docs_and_deduces_themes():
    with tempfile.TemporaryDirectory() as tmp:
        info = ingest(_docs(tmp))
        assert set(info["documents"]) == {"spec.md", "notes.txt"}
        kws = dict(info["keywords"])
        assert "invoices" in kws or "billing" in kws
        assert "Payments Spec" in info["headings"]


def test_proposal_is_labelled_and_writes_nothing():
    with tempfile.TemporaryDirectory() as tmp:
        root = _docs(tmp)
        before = sorted(p.name for p in root.iterdir())
        text = format_proposal(ingest(root))
        after = sorted(p.name for p in root.iterdir())
        assert before == after
        assert "PROPOSED" in text and "Nothing is written" in text
        assert not (root / ".pace").exists()


def test_no_documents_is_handled_gracefully():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "image.png").write_bytes(b"\x89PNG")
        text = format_proposal(ingest(Path(tmp)))
        assert "No text documents found" in text


def test_single_file_path_works():
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "readme.md"
        f.write_text("# Title\n\nsome meaningful words about robotics and sensors\n")
        info = ingest(f)
        assert info["documents"] == ["readme.md"]


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test(); print(f"PASS {test.__name__}")
    print(f"\n{len(tests)} tests passed")
