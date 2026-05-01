"""Claude Code CLI marketplace bundle and plugin install."""

from __future__ import annotations

import sys
from pathlib import Path

from agent_foundry.utils.command_runner import run_command
from agent_foundry.utils.fsutil import prune_empty_parents, unlink_or_rmtree
from agent_foundry.utils.json_io import (
    ensure_plugins_list,
    read_json_dict_or_default,
    upsert_dict_in_list_by_key,
    write_json,
)
from agent_foundry.installers.common import replace_copytree, which_cmd
from agent_foundry.registry import (
    find_registry_file,
    get_registry_plugin,
    repository_root,
)

# Synthetic marketplace under ~/.agent-foundry/ (repo need not ship marketplace.json).
CLAUDE_CLI_MARKETPLACE_NAME = "agent-foundry-local"
CLAUDE_CLI_BUNDLE_SEGMENTS = (".agent-foundry", "claude-marketplace", "local-bundle")


def _claude_bundle_root() -> Path:
    return Path.home().joinpath(*CLAUDE_CLI_BUNDLE_SEGMENTS)


def _upsert_claude_cli_marketplace_manifest(
    bundle_root: Path,
    plugin_id: str,
    *,
    version: str,
    description: str,
) -> None:
    meta_dir = bundle_root / ".claude-plugin"
    meta_dir.mkdir(parents=True, exist_ok=True)
    mpath = meta_dir / "marketplace.json"
    catalog = read_json_dict_or_default(mpath, {})
    catalog["name"] = CLAUDE_CLI_MARKETPLACE_NAME
    catalog.setdefault("owner", {"name": "agent-foundry-cli"})
    plugins_list = ensure_plugins_list(catalog)
    new_entry = {
        "name": plugin_id,
        "description": description,
        "source": f"./plugins/{plugin_id}",
        "version": version,
    }
    upsert_dict_in_list_by_key(
        plugins_list, key="name", value=plugin_id, replacement=new_entry
    )
    write_json(mpath, catalog)


def install_claude(plugin_id: str, plugin_root: Path, *, in_project: bool = False) -> None:
    """Copy bundle, register marketplace via CLI, ``claude plugin install``."""
    _ = in_project
    reg = find_registry_file()
    repo_root = repository_root(reg)
    expected = (repo_root / "plugins" / plugin_id).resolve()
    if plugin_root.resolve() != expected:
        raise RuntimeError(
            f"Plugin path mismatch: registry points to {plugin_root}, expected {expected}"
        )

    claude = which_cmd("claude")
    if not claude:
        raise RuntimeError(
            "Claude Code CLI not found on PATH (expected command: claude)."
        )

    try:
        entry = get_registry_plugin(plugin_id)
    except KeyError as e:
        raise RuntimeError(f"Plugin {plugin_id!r} missing from registry/plugins.yaml") from e
    version = entry.version or "0.0.0"
    description = entry.summary or f"agent-foundry plugin {plugin_id}"

    bundle_root = _claude_bundle_root()
    plugin_copy = bundle_root / "plugins" / plugin_id
    replace_copytree(plugin_root.resolve(), plugin_copy)
    _upsert_claude_cli_marketplace_manifest(
        bundle_root,
        plugin_id,
        version=version,
        description=description,
    )

    bundle_str = str(bundle_root.resolve())
    r_add = run_command([claude, "plugin", "marketplace", "add", bundle_str], check=False)
    if r_add.returncode != 0:
        combo = ((r_add.stderr or "") + (r_add.stdout or "")).lower()
        benign = ("already" in combo) or ("exist" in combo and "registered" in combo)
        if not benign:
            print(r_add.stdout, end="", file=sys.stderr)
            print(r_add.stderr, end="", file=sys.stderr)
            raise RuntimeError(
                "claude plugin marketplace add failed. "
                "See stderr above or run manually:\n"
                f"  claude plugin marketplace add {bundle_str}"
            )

    spec = f"{plugin_id}@{CLAUDE_CLI_MARKETPLACE_NAME}"
    r_inst = run_command([claude, "plugin", "install", spec], check=False)
    print(r_inst.stdout, end="")
    print(r_inst.stderr, end="", file=sys.stderr)
    if r_inst.returncode != 0:
        raise RuntimeError(
            "claude plugin install failed. Check Claude's stderr above. Common fixes:\n"
            f"  claude plugin marketplace list\n"
            f"  claude plugin marketplace remove {CLAUDE_CLI_MARKETPLACE_NAME}   # if stale\n"
            f"  claude plugin marketplace add {bundle_str}\n"
            f"  claude plugin install {spec}\n"
            "Or bypass the marketplace: "
            f"claude --plugin-dir {plugin_root.resolve()}"
        )
    print(
        f"Claude Code: marketplace {CLAUDE_CLI_MARKETPLACE_NAME!r} → {bundle_root}",
        file=sys.stderr,
    )


def uninstall_claude(plugin_id: str, *, in_project: bool = False) -> None:
    _ = in_project
    claude_bin = which_cmd("claude")
    spec = f"{plugin_id}@{CLAUDE_CLI_MARKETPLACE_NAME}"
    if claude_bin:
        r = run_command([claude_bin, "plugin", "uninstall", spec], check=False)
        if r.stdout:
            print(r.stdout, end="")
        if r.stderr:
            print(r.stderr, end="", file=sys.stderr)
        if r.returncode != 0:
            print(
                f"Claude: plugin uninstall ({spec}) failed or plugin was already removed.",
                file=sys.stderr,
            )
        else:
            print(f"Claude Code: uninstalled {spec}.", file=sys.stderr)
    else:
        print(
            "Claude Code CLI not on PATH; skipping `claude plugin uninstall`.",
            file=sys.stderr,
        )

    legacy_root = Path.home() / ".agent-foundry" / "claude-marketplace" / "agent-foundry"
    plugin_link = legacy_root / "plugins" / plugin_id
    if unlink_or_rmtree(plugin_link):
        print(f"Claude: removed legacy copy {plugin_link}", file=sys.stderr)
        prune_empty_parents(plugin_link.parent, stop_at=Path.home())
