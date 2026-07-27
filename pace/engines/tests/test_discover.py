"""Tests for the discover engine: reads README/stack/languages, proposes,
and writes nothing. Run: python pace/engines/tests/test_discover.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from pace.engines.discover import discover, format_proposal


def _project(tmp):
    root = Path(tmp)
    (root / "README.md").write_text("# Cool App\n\nDoes cool things.\n")
    (root / "app.py").write_text("print('hi')\n")
    (root / "pyproject.toml").write_text("[project]\nname='cool'\n")
    return root


def test_discover_reads_readme_stack_and_languages():
    with tempfile.TemporaryDirectory() as tmp:
        info = discover(_project(tmp))
        assert "Cool App" in (info["readme"] or "")
        assert "Python" in info["stack"]
        assert any(lang == "Python" for lang, _ in info["languages"])


def test_proposal_is_labelled_and_mentions_adopt_command():
    with tempfile.TemporaryDirectory() as tmp:
        text = format_proposal(discover(_project(tmp)))
        assert "PROPOSED" in text and "pace init --guided" in text


def test_discover_writes_nothing():
    with tempfile.TemporaryDirectory() as tmp:
        root = _project(tmp)
        before = sorted(p.name for p in root.iterdir())
        discover(root)
        format_proposal(discover(root))
        after = sorted(p.name for p in root.iterdir())
        assert before == after
        assert not (root / ".pace").exists()


def test_no_code_project_still_proposes():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "notes.txt").write_text("just some notes")
        text = format_proposal(discover(Path(tmp)))
        assert "non-code project" in text or "PROPOSED" in text


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test(); print(f"PASS {test.__name__}")
    print(f"\n{len(tests)} tests passed")
