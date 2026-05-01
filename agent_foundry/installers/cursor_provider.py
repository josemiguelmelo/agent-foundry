"""Cursor IDE plugin install (copied tree under ``.cursor/plugins/local``)."""

from __future__ import annotations

import sys
from pathlib import Path

from agent_foundry.utils.fsutil import prune_empty_parents, unlink_or_rmtree
from agent_foundry.utils.paths import install_base
from agent_foundry.installers.common import replace_copytree


def _safe_plugin_target(base: Path, plugin_id: str) -> Path:
    target_root = (base / ".cursor" / "plugins" / "local").resolve()
    target = (target_root / plugin_id).resolve()
    if target.parent != target_root:
        raise RuntimeError(f"Invalid plugin id for uninstall path: {plugin_id!r}")
    return target


def install_cursor(plugin_id: str, plugin_root: Path, *, in_project: bool = False) -> None:
    """
    Cursor: plugin root with ``.cursor-plugin/plugin.json`` under
    ``~/.cursor/plugins/local/<id>``.

    **Copy vs symlink:** Cursor commonly does not discover or load plugins when
    that directory is only a symlink to another tree. A real directory tree is copied;
    rerun ``install cursor`` after local plugin edits.
    """
    base = install_base(in_project=in_project)
    target = base / ".cursor" / "plugins" / "local" / plugin_id
    replace_copytree(plugin_root.resolve(), target)
    print(f"Cursor: copied plugin to {target}", file=sys.stderr)
    print(
        "Restart Cursor or run Developer: Reload Window. "
        "Re-run this command after editing the plugin in the repo.",
        file=sys.stderr,
    )


def uninstall_cursor(plugin_id: str, *, in_project: bool = False) -> None:
    """Remove ``.cursor/plugins/local/<id>`` (copied or symlink install)."""
    base = install_base(in_project=in_project)
    target = _safe_plugin_target(base, plugin_id)
    if unlink_or_rmtree(target):
        print(f"Cursor: removed {target}", file=sys.stderr)
        prune_empty_parents(target.parent, stop_at=base)
    else:
        print(f"Cursor: nothing to remove at {target}", file=sys.stderr)
    print("Restart Cursor or reload the window.", file=sys.stderr)
