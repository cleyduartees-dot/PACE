"""End-to-end CLI tests: init -> doctor -> context, through main(), not
by calling the underlying functions directly. Run directly:
python cli/tests/test_cli.py
"""

import contextlib
import io
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from cli.pace import main


def run(argv):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = main(argv)
    return code, buffer.getvalue()


def test_doctor_reports_no_instance_found():
    with tempfile.TemporaryDirectory() as tmp:
        code, out = run(["doctor", tmp])
        assert code == 1
        assert "no .pace/ instance found" in out


def test_init_then_doctor_then_context():
    with tempfile.TemporaryDirectory() as tmp:
        init_code, init_out = run([
            "init", tmp, "--name", "Demo", "--slug", "demo", "--org-ref", "demo-org",
        ])
        assert init_code == 0, init_out

        doctor_code, doctor_out = run(["doctor", tmp])
        assert doctor_code == 0, doctor_out
        assert "VALID" in doctor_out

        context_code, context_out = run(["context", tmp])
        assert context_code == 0
        assert "NAME Demo" in context_out
        assert "SLUG demo" in context_out
        assert "--- MISSION" in context_out


def test_init_twice_fails_on_the_second_call():
    with tempfile.TemporaryDirectory() as tmp:
        run(["init", tmp, "--name", "X", "--slug", "x", "--org-ref", "org"])
        code, out = run(["init", tmp, "--name", "X", "--slug", "x", "--org-ref", "org"])
        assert code == 1
        assert "init failed" in out


def test_create_then_doctor_on_a_brand_new_project():
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "brand-new"
        create_code, create_out = run([
            "create", str(target), "--name", "Brand New", "--slug", "brand-new", "--org-ref", "org",
        ])
        assert create_code == 0, create_out
        assert (target / ".git").is_dir()

        doctor_code, doctor_out = run(["doctor", str(target)])
        assert doctor_code == 0, doctor_out
        assert "VALID" in doctor_out


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"\n{len(tests)} tests passed")
