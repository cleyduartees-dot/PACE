"""PACE CLI — thin command layer delegating to the Kernel and Engines.
No logic of its own. Not yet installed as a real `pace` executable — run
as `python cli/pace.py <command> ...`; packaging is a later decision.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kernel.kernel import locate_instance, validate_instance
from services.pdl import read_pdl
from engines.project_creator import init_instance

ACTIVE_SECTIONS = [
    ("MISSION", "ACTIVE_MISSION"),
    ("VISION", "ACTIVE_VISION"),
    ("ROADMAP", "ACTIVE_ROADMAP"),
    ("SPRINT", "ACTIVE_SPRINT"),
]


def cmd_doctor(args) -> int:
    root = locate_instance(Path(args.path) if args.path else None)
    if root is None:
        print("no .pace/ instance found")
        return 1
    violations = validate_instance(root)
    if violations:
        print(f"INVALID - {len(violations)} violation(s):")
        for v in violations:
            print(f"  - {v}")
        return 1
    print(f"VALID - {root}")
    return 0


def cmd_context(args) -> int:
    root = locate_instance(Path(args.path) if args.path else None)
    if root is None:
        print("no .pace/ instance found")
        return 1

    instance = read_pdl(root / "INSTANCE.pdl")
    active = read_pdl(root / "ACTIVE_VERSIONS.pdl")

    print(f"NAME {instance.get('NAME')}")
    print(f"SLUG {instance.get('SLUG')}")
    print(f"KIND {instance.get('KIND')}")
    print(f"SCHEMA_VERSION {instance.get('SCHEMA_VERSION')}")
    if instance.get("ORG_REF"):
        print(f"ORG_REF {instance.get('ORG_REF')}")
    print()

    for label, key in ACTIVE_SECTIONS:
        relative_path = active.get(key)
        if not relative_path:
            continue
        full_path = root / relative_path
        print(f"--- {label} ({relative_path}) ---")
        if full_path.is_file():
            print(full_path.read_text(encoding="utf-8").strip())
        else:
            print("(file not found)")
        print()
    return 0


def cmd_init(args) -> int:
    try:
        root = init_instance(
            Path(args.path),
            kind=args.kind,
            name=args.name,
            slug=args.slug,
            org_ref=args.org_ref,
        )
    except (FileExistsError, ValueError) as error:
        print(f"init failed: {error}")
        return 1
    print(f"created .pace/ at {root}")
    violations = validate_instance(root)
    if violations:
        print("WARNING - the new instance is not structurally valid:")
        for v in violations:
            print(f"  - {v}")
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pace")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="validate a .pace/ instance structurally")
    doctor.add_argument("path", nargs="?", default=None)
    doctor.set_defaults(func=cmd_doctor)

    context = subparsers.add_parser("context", help="print a .pace/ instance's current context")
    context.add_argument("path", nargs="?", default=None)
    context.set_defaults(func=cmd_context)

    init = subparsers.add_parser("init", help="create a new .pace/ instance in an existing project")
    init.add_argument("path")
    init.add_argument("--kind", choices=["PROJECT", "ORGANIZATION"], default="PROJECT")
    init.add_argument("--name", required=True)
    init.add_argument("--slug", required=True)
    init.add_argument("--org-ref", dest="org_ref", default=None)
    init.set_defaults(func=cmd_init)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
