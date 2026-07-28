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
from pace.engines.handoff import generate_handoff, _root_authority
from pace.engines.rules import add_rule, list_rules
from pace.engines.memory import remember, recall, condense
from pace.engines.hooks import install_hook, uninstall_hook
from pace.engines.agent_setup import install_all
from pace.engines.decisions import capture_decision
from pace.engines.handoff import generate_handoff, _root_authority, _ensure_agents_pointer

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
    owner = _prompt("Who is the decision-maker / owner? (ROOT_AUTHORITY)")
    if owner:
        extra["owner"] = owner
        role = _prompt("Their role (e.g. President, Founder, Lead)")
        if role:
            extra["owner_role"] = role
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
    if args.owner:
        extra["owner"] = args.owner
    if args.owner_role:
        extra["owner_role"] = args.owner_role
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


def _mark_superseded(text: str, new_name: str) -> str:
    """Stamp a prior version file as no longer current: set its STATUS to
    SUPERSEDED and add SUPERSEDED_BY, so each file is self-describing and
    does not depend solely on ACTIVE_VERSIONS. This is a lifecycle metadata
    update (like the requests STATUS exception in the contract); the file's
    knowledge content is never rewritten."""
    trailing_nl = text.endswith("\n")
    out, status_done, supby_done = [], False, False
    for line in text.splitlines():
        stripped = line.strip().upper()
        if stripped.startswith("SUPERSEDED_BY "):
            supby_done = True
        if stripped.startswith("STATUS ") and not status_done:
            out.append("STATUS SUPERSEDED")
            status_done = True
            continue
        if line.strip() == "END" and not supby_done:
            out.append(f"SUPERSEDED_BY {new_name}")
            supby_done = True
        out.append(line)
    return "\n".join(out) + ("\n" if trailing_nl else "")


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

    try:
        prior = current_path.read_text(encoding="utf-8")
        stamped = _mark_superseded(prior, new_name)
        if stamped != prior:
            current_path.write_text(stamped, encoding="utf-8")
    except OSError:
        pass

    active[key] = f"{section}/{new_name}"
    lines = [f"{k} {active.get(k, '')}".rstrip() for k in _ACTIVE_ORDER]
    lines.append("END")
    active_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"superseded {section}: {current_path.name} -> {new_name} (active version updated)")
    return 0


def cmd_condense(args) -> int:
    root = locate_instance(Path(args.path) if args.path else None)
    if root is None:
        print("no .pace/ instance found")
        return 1
    n, archive = condense(root, keep=args.keep)
    if n == 0:
        print("nothing to condense (continuity log is within the limit)")
    else:
        print(f"condensed {n} old note(s) into {archive.name}; working log trimmed to the last {args.keep}")
    return 0


def cmd_update(args) -> int:
    """One-step self-update: the CLI's 'press here' (REQUEST-0014)."""
    import subprocess
    base = [sys.executable, "-m", "pip", "install", "--upgrade", "pace-engine"]
    print("updating pace-engine (pip install --upgrade pace-engine)...")
    result = subprocess.run(base)
    if result.returncode != 0:
        # Externally-managed environments (Debian/Ubuntu PEP 668) reject the
        # plain install; retry once with the escape hatch instead of failing.
        print("retrying for an externally-managed environment (--break-system-packages)...")
        result = subprocess.run(base + ["--break-system-packages"])
    if result.returncode == 0:
        print("pace is up to date.")
    else:
        print("update failed - try manually: pip install --upgrade pace-engine --break-system-packages")
    return result.returncode


def cmd_hook(args) -> int:
    root = locate_instance(Path(args.path) if args.path else None)
    if root is None:
        print("no .pace/ instance found")
        return 1
    try:
        if args.hook_command == "install":
            hook = install_hook(root)
            print(f"pre-commit hook installed at {hook} - commits that break the contract will be blocked")
        else:
            hook = uninstall_hook(root)
            print(f"pre-commit hook neutralized at {hook}" if hook else "no hook to uninstall")
    except (FileNotFoundError, FileExistsError) as error:
        print(f"hook {args.hook_command} failed: {error}")
        return 1
    return 0


def cmd_roadmap(args) -> int:
    root = locate_instance(Path(args.path) if args.path else None)
    if root is None:
        print("no .pace/ instance found")
        return 1
    from pace.engines.roadmap import parse_roadmap, drift
    import json as _json
    items = parse_roadmap(root)
    if args.against:
        try:
            tracker = _json.loads(Path(args.against).read_text(encoding="utf-8"))
        except Exception as error:
            print(f"could not read tracker export: {error}")
            return 1
        d = drift(items, tracker)
        if not d["missing"] and not d["status_mismatch"]:
            print("tracker is in sync with the roadmap.")
            return 0
        if d["missing"]:
            print("Roadmap items missing from the tracker: " + ", ".join(d["missing"]))
        for m in d["status_mismatch"]:
            state = "DONE" if m["roadmap_done"] else "open"
            print(f"  item {m['number']}: roadmap says {state}, tracker says '{m['tracker_status']}'")
        return 1
    if args.json:
        print(_json.dumps(items, indent=2))
        return 0
    for i in items:
        if args.open and i["done"]:
            continue
        mark = "[x]" if i["done"] else "[ ]"
        print(f"{mark} {i['number']}  {i['title']}")
    return 0


def cmd_ingest(args) -> int:
    """Read documents and PROPOSE what PACE deduced (read-only)."""
    from pace.engines.ingest import ingest, format_proposal
    root = Path(args.path) if args.path else Path.cwd()
    if not root.exists():
        print(f"ingest failed: {root} does not exist")
        return 1
    print(format_proposal(ingest(root)))
    return 0


def cmd_discover(args) -> int:
    """Auto-read an existing project and PROPOSE a draft .pace/ (read-only)."""
    from pace.engines.discover import discover, format_proposal
    root = Path(args.path) if args.path else Path.cwd()
    if not root.is_dir():
        print(f"discover failed: {root} is not a directory")
        return 1
    print(format_proposal(discover(root)))
    return 0


def cmd_watch(args) -> int:
    root = locate_instance(Path(args.path) if args.path else None)
    if root is None:
        print("no .pace/ instance found")
        return 1
    from pace.engines.watch import watch_once, watch_loop
    if args.once:
        _, msgs = watch_once(root)
        for m in msgs:
            print(f"[pace watch] {m}")
        if not msgs:
            print("[pace watch] up to date; contract VALID; nothing to report")
        return 0
    print(f"[pace watch] watching {root} every {args.interval}s (Ctrl-C to stop)")
    try:
        watch_loop(root, args.interval, printer=lambda m: print(f"[pace watch] {m}"))
    except KeyboardInterrupt:
        print("\n[pace watch] stopped.")
    return 0


def cmd_capture(args) -> int:
    """Record an approved decision immediately - the conversational-capture
    verb so a decision never lives only in the chat (RULE-0008)."""
    root = locate_instance(Path(args.path) if args.path else None)
    if root is None:
        print("no .pace/ instance found")
        return 1
    decided_by = _root_authority(root) or ""
    try:
        out = capture_decision(root, args.title, detail=args.why or "", decided_by=decided_by)
    except ValueError as error:
        print(f"capture failed: {error}")
        return 1
    print(f"captured {out.name} in {out.parent}")
    return 0


def cmd_check(args) -> int:
    """Fast, quiet per-message verification: is PACE here, is it current.
    Silent when there is no .pace/ (so it is safe as a global hook)."""
    root = locate_instance(Path(args.path) if args.path else None)
    if root is None:
        return 0
    from pace.services.update_check import latest_version_cached, _parse
    from pace.services.version import PACE_VERSION
    instance = read_pdl(root / "INSTANCE.pdl")
    name = instance.get("NAME", "this project")
    print(f"PACE active: {name} (engine {PACE_VERSION}). Consult `pace handoff` "
          "for the project's memory before acting; capture approved decisions with `pace capture` the moment they happen.")
    latest = latest_version_cached(root)
    if latest and _parse(latest) > _parse(PACE_VERSION):
        print(f"WARN: a newer PACE engine ({latest}) is available - run `pace update`.")
    return 0


def cmd_agent(args) -> int:
    root = locate_instance(Path(args.path) if args.path else None)
    if root is None:
        print("no .pace/ instance found")
        return 1
    results = install_all(root, _ensure_agents_pointer)
    print("Wired PACE into every client that can be wired:")
    for label, path, enforced, created in results:
        mark = "installed" if created else "already present"
        print(f"  - {label}: {path} ({mark})")
    print("\nEnforced per-message only where the client supports a hook "
          "(Claude Code). Elsewhere PACE relies on the instruction being read.")
    return 0


def cmd_rule(args) -> int:
    root = locate_instance(Path(args.path) if args.path else None)
    if root is None:
        print("no .pace/ instance found")
        return 1
    if args.rule_command == "list":
        print(list_rules(root))
        return 0
    approved_by = _root_authority(root) or ""
    try:
        out = add_rule(
            root, args.scope, args.statement,
            rationale=args.rationale or "",
            promoted_from=args.from_ref or "",
            approved_by=approved_by,
        )
    except ValueError as error:
        print(f"rule add failed: {error}")
        return 1
    print(f"recorded {out.name} in {out.parent}")
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
    init.add_argument("--owner", default=None, help="the decision-maker / ROOT_AUTHORITY to seed as an ACTOR")
    init.add_argument("--owner-role", dest="owner_role", default=None, help="the owner role label (President, Founder, Lead, ...)")
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

    condense = subparsers.add_parser("condense", help="archive old continuity notes so the working log stays lean (nothing discarded)")
    condense.add_argument("--keep", type=int, default=20, help="how many recent notes to keep in the working log")
    condense.add_argument("path", nargs="?", default=None)
    condense.set_defaults(func=cmd_condense)

    update = subparsers.add_parser("update", help="update pace-engine itself to the latest version (one step)")
    update.set_defaults(func=cmd_update)

    hook = subparsers.add_parser("hook", help="manage the git pre-commit guardian that blocks contract-breaking commits")
    hook_sub = hook.add_subparsers(dest="hook_command", required=True)
    hook_install = hook_sub.add_parser("install", help="install the pre-commit hook (runs pace doctor on every commit)")
    hook_install.add_argument("path", nargs="?", default=None)
    hook_install.set_defaults(func=cmd_hook)
    hook_uninstall = hook_sub.add_parser("uninstall", help="neutralize the PACE pre-commit hook")
    hook_uninstall.add_argument("path", nargs="?", default=None)
    hook_uninstall.set_defaults(func=cmd_hook)

    roadmap = subparsers.add_parser("roadmap", help="show the roadmap as data, or detect drift vs a tracker export (--against file.json)")
    roadmap.add_argument("--json", action="store_true", help="emit the roadmap items as JSON")
    roadmap.add_argument("--open", action="store_true", help="show only unfinished items")
    roadmap.add_argument("--against", default=None, help="a JSON export of tracker tasks to check for drift")
    roadmap.add_argument("path", nargs="?", default=None)
    roadmap.set_defaults(func=cmd_roadmap)

    ingest = subparsers.add_parser("ingest", help="read documents (README, notes, specs, PDFs) and PROPOSE what PACE deduced (writes nothing)")
    ingest.add_argument("path", nargs="?", default=None)
    ingest.set_defaults(func=cmd_ingest)

    discover = subparsers.add_parser("discover", help="auto-read an existing project (README, code, git) and PROPOSE a draft .pace/ (writes nothing)")
    discover.add_argument("path", nargs="?", default=None)
    discover.set_defaults(func=cmd_discover)

    watch = subparsers.add_parser("watch", help="continuously watch the .pace/ instance and warn on drift, breakage or a new engine version")
    watch.add_argument("--interval", type=int, default=5, help="seconds between checks")
    watch.add_argument("--once", action="store_true", help="run a single check and exit")
    watch.add_argument("path", nargs="?", default=None)
    watch.set_defaults(func=cmd_watch)

    capture = subparsers.add_parser("capture", help="record an approved decision immediately (so it never lives only in the chat)")
    capture.add_argument("title")
    capture.add_argument("--why", default="", help="the rationale behind the decision")
    capture.add_argument("path", nargs="?", default=None)
    capture.set_defaults(func=cmd_capture)

    check = subparsers.add_parser("check", help="fast per-message verification: is PACE here and current (safe to run on every message)")
    check.add_argument("path", nargs="?", default=None)
    check.set_defaults(func=cmd_check)

    agent = subparsers.add_parser("agent", help="wire PACE into AI clients (Claude Code hook, Cursor rule, AGENTS.md)")
    agent_sub = agent.add_subparsers(dest="agent_command", required=True)
    agent_install = agent_sub.add_parser("install", help="install the per-message hook / rules in every client that supports it")
    agent_install.add_argument("path", nargs="?", default=None)
    agent_install.set_defaults(func=cmd_agent)

    rule = subparsers.add_parser("rule", help="record or list approved governance rules an AI must obey")
    rule_sub = rule.add_subparsers(dest="rule_command", required=True)
    rule_add = rule_sub.add_parser("add", help="record a new approved rule (never re-asked once set)")
    rule_add.add_argument("--scope", required=True, choices=["PACE", "ORGANIZATION", "PROJECT"])
    rule_add.add_argument("--statement", required=True)
    rule_add.add_argument("--rationale", default="")
    rule_add.add_argument("--from", dest="from_ref", default="",
                          help="what this rule was promoted from (a request or correction)")
    rule_add.add_argument("path", nargs="?", default=None)
    rule_add.set_defaults(func=cmd_rule)
    rule_list = rule_sub.add_parser("list", help="list approved rules grouped by scope")
    rule_list.add_argument("path", nargs="?", default=None)
    rule_list.set_defaults(func=cmd_rule)

    create = subparsers.add_parser("create", help="generate a brand-new project governed by PACE from scratch")
    create.add_argument("path")
    create.add_argument("--name", required=True)
    create.add_argument("--slug", required=True)
    create.add_argument("--org-ref", dest="org_ref", required=True)
    create.set_defaults(func=cmd_create)

    return parser


def _menu_text(question, command):
    text = _prompt(question).strip()
    if not text:
        print("(cancelado)")
        return 0
    return main([command, text, "."])


def run_menu() -> int:
    """Guided menu for anyone - `pace` with no arguments. Maps plain
    choices to the underlying commands so a newcomer never has to memorize
    them (REQUEST-0020)."""
    actions = [
        ("Empezar / configurar la memoria de este proyecto", lambda: main(["init", "--guided", "."])),
        ("Ver el estado del proyecto", lambda: main(["handoff", "."])),
        ("Guardar una nota", lambda: _menu_text("Que quieres anotar?", "remember")),
        ("Ver la memoria guardada", lambda: main(["recall", "."])),
        ("Registrar una decision aprobada", lambda: _menu_text("Que se decidio?", "capture")),
        ("Comprobar que la memoria esta bien", lambda: main(["doctor", "."])),
    ]
    print("\n  PACE - que quieres hacer?\n")
    for i, (label, _) in enumerate(actions, 1):
        print(f"    {i}) {label}")
    print("    0) Salir\n")
    choice = _prompt("Elige un numero").strip()
    if choice in ("", "0"):
        print("Hasta luego.")
        return 0
    try:
        idx = int(choice)
    except ValueError:
        idx = -1
    if 1 <= idx <= len(actions):
        return actions[idx - 1][1]()
    print("Opcion no valida. Corre `pace` de nuevo.")
    return 1


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        if sys.stdin.isatty():
            return run_menu()
        build_parser().print_help()
        return 0
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
