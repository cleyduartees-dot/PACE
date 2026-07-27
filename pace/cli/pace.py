"""PACE CLI - thin command layer delegating to the Kernel and Engines.

Beyond argument handling, the only logic here is the guided intake: an
interactive setup that seeds a project's memory from the owner's answers.
Run as `python cli/pace.py <command> ...`, or install and run `pace ...`.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pace.kernel.kernel import locate_instance, validate_instance
from pace.services.pdl import read_pdl
from pace.engines.project_creator import init_instance, create_project
from pace.engines.handoff import generate_handoff
from pace.engines.memory import remember, recall

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


def _slugify(name: str) -> str:
    slug = "".join(c if c.isalnum() else "-" for c in name.lower())
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "project"


def _prompt(text: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        value = input(f"{text}{suffix}\n> ").strip()
    except EOFError:
        value = ""
    return value or default


def run_guided_intake(kind, name, slug, org_ref):
    """Interactive setup: ask a few questions and seed mission / vision /
    roadmap / sprint. The AI (or the owner) answers; nothing is invented.
    Returns the resolved identity plus an `extra` dict of seeded content."""
    print("\nPACE guided setup - a few questions to seed your project's memory.")
    print("Press Enter to accept a [default] or to skip a question.\n")

    if not name:
        name = _prompt("Project name") or "Unnamed project"
    kind_in = _prompt("Kind (PROJECT / ORGANIZATION)", kind or "PROJECT").upper()
    kind = "ORGANIZATION" if kind_in.startswith("O") else "PROJECT"
    if kind == "PROJECT" and not org_ref:
        org_ref = _prompt("Organization it belongs to (org ref)") or "org"
    if not slug:
        slug = _prompt("Slug", _slugify(name))

    extra = {}
    mission = _prompt("Why does this project exist? (mission)")
    if mission:
        extra["mission"] = mission
    vision = _prompt("Where is it going? (vision)")
    if vision:
        extra["vision"] = vision
    roadmap = _prompt("What is pending? (roadmap - main items)")
    if roadmap:
        extra["roadmap"] = roadmap
    sprint = _prompt("What are you working on right now? (current sprint)")
    if sprint:
        extra["sprint"] = sprint
    return kind, name, slug, org_ref, extra


def cmd_init(args) -> int:
    kind, name, slug, org_ref = args.kind, args.name, args.slug, args.org_ref
    extra = {}
    if args.guided:
        kind, name, slug, org_ref, extra = run_guided_intake(kind, name, slug, org_ref)

    if not name:
        print("init failed: --name is required (or use --guided)")
        return 1
    if not slug:
        slug = _slugify(name)

    try:
        root = init_instance(
            Path(args.path), kind=kind, name=name, slug=slug, org_ref=org_ref, **extra
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


def cmd_create(args) -> int:
    try:
        root = create_project(
            Path(args.path),
            name=args.name,
            slug=args.slug,
            org_ref=args.org_ref,
        )
    except FileExistsError as error:
        print(f"create failed: {error}")
        return 1
    print(f"created project at {root.parent}")
    violations = validate_instance(root)
    if violations:
        print("WARNING - the new instance is not structurally valid:")
        for v in violations:
            print(f"  - {v}")
        return 1
    return 0


def cmd_handoff(args) -> int:
    root = locate_instance(Path(args.path) if args.path else None)
    if root is None:
        print("no .pace/ instance found")
        return 1
    out = generate_handoff(root)
    print(f"handoff regenerated at {out}\n")
    print(out.read_text(encoding="utf-8"))
    return 0


def cmd_remember(args) -> int:
    root = locate_instance(Path(args.path) if args.path else None)
    if root is None:
        print("no .pace/ instance found")
        return 1
    out = remember(root, args.text)
    print(f"remembered in {out}")
    return 0


def cmd_recall(args) -> int:
    root = locate_instance(Path(args.path) if args.path else None)
    if root is None:
        print("no .pace/ instance found")
        return 1
    print(recall(root))
    return 0



_SECTION_KEYS = {
    "mission": "ACTIVE_MISSION",
    "vision": "ACTIVE_VISION",
    "roadmap": "ACTIVE_ROADMAP",
    "sprint": "ACTIVE_SPRINT",
}
_ACTIVE_ORDER = ["ACTIVE_MISSION", "ACTIVE_VISION", "ACTIVE_ROADMAP", "ACTIVE_SPRINT"]


def _bump_version(ver: str) -> str:
    parts = ver.split(".")
    try:
        parts[-1] = str(int(parts[-1]) + 1)
    except ValueError:
        return ver + "1"
    return ".".join(parts)


def cmd_supersede(args) -> int:
    root = locate_instance(Path(args.path) if args.path else None)
    if root is None:
        print("no .pace/ instance found")
        return 1
    section = args.section.lower()
    key = _SECTION_KEYS.get(section)
    if key is None:
        print(f"supersede failed: unknown section '{args.section}'")
        return 1

    active_file = root / "ACTIVE_VERSIONS.pdl"
    active = read_pdl(active_file)
    current_rel = active.get(key)
    if not current_rel:
        print(f"supersede failed: no active {section}")
        return 1
    current_path = root / current_rel
    stem = current_path.name[:-4] if current_path.name.endswith(".pdl") else current_path.name
    prefix, _, ver = stem.rpartition("_")
    if not prefix:
        prefix, ver = stem, "1"

    new_ver = _bump_version(ver)
    new_name = f"{prefix}_{new_ver}.pdl"
    while (current_path.parent / new_name).exists():
        new_ver = _bump_version(new_ver)
        new_name = f"{prefix}_{new_ver}.pdl"
    new_path = current_path.parent / new_name

    version_field = section.upper() + "_VERSION"
    content_field = section.upper()
    body = (
        f"{version_field} {new_ver}\n\n"
        f"STATUS APPROVED\n\n"
        f"SUPERSEDES {current_path.name}\n\n"
        f"{content_field} {args.content}\n\n"
        f"END\n"
    )
    new_path.parent.mkdir(parents=True, exist_ok=True)
    new_path.write_text(body, encoding="utf-8")

    active[key] = f"{section}/{new_name}"
    lines = [f"{k} {active.get(k, '')}".rstrip() for k in _ACTIVE_ORDER]
    lines.append("END")
    active_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"superseded {section}: {current_path.name} -> {new_name} (active version updated)")
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
    init.add_argument("--name", default=None)
    init.add_argument("--slug", default=None)
    init.add_argument("--org-ref", dest="org_ref", default=None)
    init.add_argument("--guided", action="store_true",
                      help="interactive guided setup that seeds mission/vision/roadmap/sprint")
    init.set_defaults(func=cmd_init)

    handoff = subparsers.add_parser("handoff", help="regenerate the AI-onboarding handoff for a .pace/ instance")
    handoff.add_argument("path", nargs="?", default=None)
    handoff.set_defaults(func=cmd_handoff)

    remember = subparsers.add_parser("remember", help="append a continuity note to the project's working memory")
    remember.add_argument("text")
    remember.add_argument("path", nargs="?", default=None)
    remember.set_defaults(func=cmd_remember)

    recall = subparsers.add_parser("recall", help="print the project's working/continuity memory")
    recall.add_argument("path", nargs="?", default=None)
    recall.set_defaults(func=cmd_recall)

    supersede = subparsers.add_parser("supersede", help="update a protected section by creating a new version (never edits in place)")
    supersede.add_argument("section", choices=["mission", "vision", "roadmap", "sprint"])
    supersede.add_argument("content")
    supersede.add_argument("path", nargs="?", default=None)
    supersede.set_defaults(func=cmd_supersede)

    create = subparsers.add_parser("create", help="generate a brand-new project governed by PACE from scratch")
    create.add_argument("path")
    create.add_argument("--name", required=True)
    create.add_argument("--slug", required=True)
    create.add_argument("--org-ref", dest="org_ref", required=True)
    create.set_defaults(func=cmd_create)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
