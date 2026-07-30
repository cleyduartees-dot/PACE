"""Tests for stack templates (pace create --template)."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from pace.engines.templates import list_templates, apply_template


def test_list_templates_includes_python_and_node():
    t = list_templates()
    assert "python" in t and "node" in t


def test_apply_template_copies_files():
    with tempfile.TemporaryDirectory() as tmp:
        copied = apply_template(tmp, "python")
        assert "pyproject.toml" in copied
        assert (Path(tmp) / "main.py").is_file()


def test_apply_unknown_template_raises():
    with tempfile.TemporaryDirectory() as tmp:
        try:
            apply_template(tmp, "cobol")
            assert False, "should have raised"
        except ValueError:
            pass
