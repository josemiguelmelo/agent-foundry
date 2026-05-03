"""Cursor IDE plugin install (copied tree under ``.cursor/plugins/local`` globally)."""

from __future__ import annotations

import sys
from pathlib import Path

from agent_foundry.installers.common import replace_copytree
from agent_foundry.installers.cursor_cli.install import (
    install_cursor_cli,
    uninstall_cursor_cli,
)
from agent_foundry.utils.fsutil import prune_empty_parents, unlink_or_rmtree
from agent_foundry.utils.paths import install_base


def _safe_plugin_target(base: Path, plugin_id: str) -> Path:
    target_root = (base / ".cursor" / "plugins" / "local").resolve()
    target = (target_root / plugin_id).resolve()
    if target.parent != target_root:
        raise RuntimeError(f"Invalid plugin id for uninstall path: {plugin_id!r}")
    return target


def install_cursor(
    plugin_id: str,
    plugin_root: Path,
    *,
    in_project: bool = False,
    force: bool = False,
) -> None:
    """
    Global: plugin root with ``.cursor-plugin/plugin.json`` under
    ``~/.cursor/plugins/local/<id>`` (full tree copy).

    Project (``--in-project``): Cursor does not load ``./.cursor/plugins/local/`` like
    the user-level IDE path; skills and agents are mirrored into ``./.cursor/skills/``
    and ``./.cursor/agents/`` using the same workflow as ``install cursor-cli``.

    **Copy vs symlink (global):** Cursor commonly does not discover or load plugins when
    that directory is only a symlink to another tree. A real directory tree is copied;
    rerun ``install cursor`` after local plugin edits.
    """
    if in_project:
        print(
            "Cursor: --in-project mirrors skills/agents under .cursor/ "
            "(project .cursor/plugins/local is not used by the IDE).",
            file=sys.stderr,
        )
        install_cursor_cli(plugin_id, plugin_root, in_project=True, force=force)
        return

    base = install_base(in_project=False)
    target = base / ".cursor" / "plugins" / "local" / plugin_id
    replace_copytree(plugin_root.resolve(), target)
    print(f"Cursor: copied plugin to {target}", file=sys.stderr)
    print(
        "Restart Cursor or run Developer: Reload Window. "
        "Re-run this command after editing the plugin in the repo.",
        file=sys.stderr,
    )


def uninstall_cursor(plugin_id: str, *, in_project: bool = False) -> None:
    """Global: remove ``.cursor/plugins/local/<id>``. Project: mirror uninstall + legacy path."""
    if in_project:
        uninstall_cursor_cli(plugin_id, in_project=True)
        base = install_base(in_project=True)
        legacy = _safe_plugin_target(base, plugin_id)
        if unlink_or_rmtree(legacy):
            print(
                f"Cursor: removed legacy plugin copy at {legacy}",
                file=sys.stderr,
            )
            prune_empty_parents(legacy.parent, stop_at=base)
        print("Restart Cursor or reload the window.", file=sys.stderr)
        return

    base = install_base(in_project=False)
    target = _safe_plugin_target(base, plugin_id)
    if unlink_or_rmtree(target):
        print(f"Cursor: removed {target}", file=sys.stderr)
        prune_empty_parents(target.parent, stop_at=base)
    else:
        print(f"Cursor: nothing to remove at {target}", file=sys.stderr)
    print("Restart Cursor or reload the window.", file=sys.stderr)
