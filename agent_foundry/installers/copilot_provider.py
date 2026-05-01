"""GitHub Copilot CLI plugin install/uninstall."""

from __future__ import annotations

import sys
from pathlib import Path

from agent_foundry.core.errors import UsageError
from agent_foundry.utils.command_runner import run_command
from agent_foundry.installers.common import which_cmd


def install_copilot(plugin_id: str, plugin_root: Path, *, in_project: bool = False) -> None:
    """GitHub Copilot CLI: `copilot plugin install <path>`."""
    if in_project:
        raise UsageError(
            "Copilot CLI plugins are installed in user scope only; "
            "--in-project is not supported for provider copilot."
        )
    copilot = which_cmd("copilot")
    if not copilot:
        raise RuntimeError(
            "Copilot CLI not found on PATH (expected command: copilot). "
            "Install GitHub Copilot CLI per Microsoft docs."
        )
    path = plugin_root.resolve()
    run_command([copilot, "plugin", "install", str(path)], check=True, capture_output=False)
    print("Copilot CLI: plugin install completed.", file=sys.stderr)


def uninstall_copilot(plugin_id: str, *, in_project: bool = False) -> None:
    """GitHub Copilot CLI: ``copilot plugin uninstall <name>``."""
    if in_project:
        raise UsageError(
            "Copilot CLI plugins are installed in user scope only; "
            "--in-project is not supported for provider copilot."
        )
    copilot = which_cmd("copilot")
    if not copilot:
        raise RuntimeError(
            "Copilot CLI not found on PATH (expected command: copilot)."
        )
    r = run_command([copilot, "plugin", "uninstall", plugin_id], check=False)
    if r.stdout:
        print(r.stdout, end="")
    if r.stderr:
        print(r.stderr, end="", file=sys.stderr)
    if r.returncode != 0:
        print(
            "Copilot: uninstall failed or plugin may not be installed.",
            file=sys.stderr,
        )
    else:
        print("Copilot CLI: plugin uninstall completed.", file=sys.stderr)
