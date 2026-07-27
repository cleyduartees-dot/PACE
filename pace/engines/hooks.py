"""Hooks engine - the Active Guardian standing at the git gate.

`pace hook install` writes a pre-commit hook that runs `pace doctor` and
blocks the commit when the .pace/ instance violates its contract, so an
AI (or a human) physically cannot commit a broken instance. Install is
idempotent; uninstall neutralizes our hook without touching a hook PACE
did not write.
"""

from pathlib import Path

MARKER = "# managed-by: pace (Active Guardian pre-commit hook)"

HOOK_BODY = f"""#!/bin/sh
{MARKER}
echo "[pace] pre-commit: validating .pace/ against its contract..."
if command -v pace >/dev/null 2>&1; then
  exec pace doctor
fi
if command -v python >/dev/null 2>&1; then
  exec python -m pace.cli.pace doctor
fi
exec python3 -m pace.cli.pace doctor
"""


def _hook_path(instance_root: Path):
    repo = Path(instance_root).parent
    git_dir = repo / ".git"
    if not git_dir.is_dir():
        return None
    hooks = git_dir / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    return hooks / "pre-commit"


def install_hook(instance_root: Path):
    """Install (or refresh) the PACE pre-commit hook. Returns the hook
    path, or raises if there is a pre-existing hook PACE does not own."""
    hook = _hook_path(instance_root)
    if hook is None:
        raise FileNotFoundError("no .git repository next to this .pace/ instance")
    if hook.exists() and MARKER not in hook.read_text(encoding="utf-8", errors="replace"):
        raise FileExistsError(
            f"a pre-commit hook already exists at {hook} and PACE did not "
            "write it - merge it manually (add `pace doctor` to it)"
        )
    hook.write_text(HOOK_BODY, encoding="utf-8", newline="\n")
    hook.chmod(0o755)
    return hook


def uninstall_hook(instance_root: Path):
    """Neutralize our hook (overwrite with a no-op). Refuses to touch a
    hook PACE did not write. Returns the hook path or None if absent."""
    hook = _hook_path(instance_root)
    if hook is None or not hook.exists():
        return None
    if MARKER not in hook.read_text(encoding="utf-8", errors="replace"):
        raise FileExistsError(f"the hook at {hook} was not written by PACE - not touching it")
    hook.write_text(f"#!/bin/sh\n{MARKER} (uninstalled)\nexit 0\n", encoding="utf-8", newline="\n")
    hook.chmod(0o755)
    return hook
