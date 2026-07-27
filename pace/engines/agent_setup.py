"""Agent setup - wiring PACE into an AI client so it is consulted
automatically, not just when the AI remembers to.

Two levers, by honesty of enforcement:
- Claude Code (and hook-capable agents): a UserPromptSubmit hook that runs
  `pace check` on EVERY user message - real enforcement, the client fires
  it. Written into .claude/settings.json, merged, never clobbering other
  settings.
- Every other surface (Cursor, Copilot, web chats): AGENTS.md at the repo
  root is the strongest lever available - a mandatory instruction the AI
  reads. Convention, not enforcement, and we say so.
"""

import json
from pathlib import Path

CLAUDE_SETTINGS_REL = ".claude/settings.json"
CHECK_COMMAND = "pace check"


def install_claude_hook(instance_root):
    """Merge a UserPromptSubmit hook that runs `pace check` into the repo's
    .claude/settings.json. Idempotent; preserves any existing settings."""
    repo = Path(instance_root).parent
    path = repo / CLAUDE_SETTINGS_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            data = {}
    hooks = data.setdefault("hooks", {})
    groups = hooks.setdefault("UserPromptSubmit", [])
    present = any(
        isinstance(g, dict) and any(
            isinstance(h, dict) and h.get("command") == CHECK_COMMAND
            for h in g.get("hooks", [])
        )
        for g in groups
    )
    if not present:
        groups.append({"hooks": [{"type": "command", "command": CHECK_COMMAND}]})
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path, (not present)


CURSOR_RULE_REL = ".cursor/rules/pace.mdc"

CURSOR_RULE = """---
description: PACE project memory - consult before acting
alwaysApply: true
---
This project is governed by PACE (pip install pace-engine).

At the start of a session run `pace handoff` and obey it. On every message,
before acting, run `pace check`. Do not ask the owner to re-explain anything
the handoff already answers. Capture approved decisions immediately with `pace capture` so they
never live only in the chat. Update protected sections only with
`pace supersede`, never by editing versioned files in place.
"""


def install_cursor_rule(instance_root):
    """Write an always-applied Cursor rule pointing at PACE. Cursor injects
    it into every request - convention, strong, but not a code hook."""
    repo = Path(instance_root).parent
    path = repo / CURSOR_RULE_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    existed = path.exists()
    path.write_text(CURSOR_RULE, encoding="utf-8")
    return path, (not existed)


def install_all(instance_root, ensure_agents):
    """Wire PACE into every client that can be wired. Returns a list of
    (label, path, enforced, created) so the caller can report honestly."""
    results = []
    settings_path, created = install_claude_hook(instance_root)
    results.append(("Claude Code (per-message hook, ENFORCED)", settings_path, True, created))
    cursor_path, created = install_cursor_rule(instance_root)
    results.append(("Cursor (always-applied rule, convention)", cursor_path, False, created))
    agents = ensure_agents(instance_root)
    if agents is not None:
        results.append(("AGENTS.md (universal instruction, convention)", agents, False, True))
    return results
