"""OpenAI Codex plugin layout and marketplace manifest."""

from __future__ import annotations

import sys
from pathlib import Path

from agent_foundry.utils.fsutil import prune_empty_parents, unlink_or_rmtree
from agent_foundry.utils.json_io import (
    ensure_plugins_list,
    read_json_dict_or_default,
    remove_dicts_from_list_by_key,
    read_json_dict_strict,
    upsert_dict_in_list_by_key,
    write_json,
)
from agent_foundry.installers.common import replace_copytree
from agent_foundry.utils.paths import install_base


def _safe_plugin_target(base: Path, plugin_id: str) -> Path:
    target_root = (base / ".codex" / "plugins").resolve()
    target = (target_root / plugin_id).resolve()
    if target.parent != target_root:
        raise RuntimeError(f"Invalid plugin id for uninstall path: {plugin_id!r}")
    return target


def install_codex(plugin_id: str, plugin_root: Path, *, in_project: bool = False) -> None:
    """
    OpenAI Codex: personal marketplace under ``~/.agents/plugins/marketplace.json``,
    plugin copies under ``~/.codex/plugins/<name>``; ``in_project`` mirrors under cwd.
    """
    base = install_base(in_project=in_project)
    codex_plugins = base / ".codex" / "plugins" / plugin_id
    replace_copytree(plugin_root.resolve(), codex_plugins)

    agents_plugins = base / ".agents" / "plugins"
    marketplace_path = agents_plugins / "marketplace.json"

    rel_path = f"./.codex/plugins/{plugin_id}"
    new_entry = {
        "name": plugin_id,
        "source": {"source": "local", "path": rel_path},
        "policy": {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        },
        "category": "Productivity",
    }

    default = {
        "name": "agent-foundry",
        "interface": {"displayName": "Agent Foundry"},
        "plugins": [],
    }
    data = read_json_dict_or_default(marketplace_path, default)
    plugins_list = ensure_plugins_list(data)
    upsert_dict_in_list_by_key(
        plugins_list, key="name", value=plugin_id, replacement=new_entry
    )
    write_json(marketplace_path, data)
    print(f"Codex: copied plugin to {codex_plugins}", file=sys.stderr)
    print(f"Codex: updated {marketplace_path}", file=sys.stderr)
    print("Restart Codex to load the marketplace entry.", file=sys.stderr)


def uninstall_codex(plugin_id: str, *, in_project: bool = False) -> None:
    """Remove ``.codex/plugins/<id>`` and drop marketplace row."""
    base = install_base(in_project=in_project)
    codex_plugins = _safe_plugin_target(base, plugin_id)
    if unlink_or_rmtree(codex_plugins):
        print(f"Codex: removed {codex_plugins}", file=sys.stderr)
        prune_empty_parents(codex_plugins.parent, stop_at=base)
    else:
        print(f"Codex: no directory at {codex_plugins}", file=sys.stderr)

    marketplace_path = base / ".agents" / "plugins" / "marketplace.json"
    if not marketplace_path.is_file():
        print(f"Codex: no marketplace file at {marketplace_path}", file=sys.stderr)
        print("Restart Codex if it is running.", file=sys.stderr)
        return

    data = read_json_dict_strict(marketplace_path)
    plugins_list = ensure_plugins_list(data)
    data["plugins"], removed_n = remove_dicts_from_list_by_key(
        plugins_list, key="name", value=plugin_id
    )
    write_json(marketplace_path, data)

    if removed_n:
        print(
            f"Codex: removed {removed_n} marketplace entr(y/ies) named {plugin_id!r}",
            file=sys.stderr,
        )
    else:
        print(
            f"Codex: no marketplace entry named {plugin_id!r}",
            file=sys.stderr,
        )
    print("Restart Codex if it is running.", file=sys.stderr)
