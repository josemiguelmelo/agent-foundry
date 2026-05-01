"""State and ownership tracking for Cursor CLI plugin mirroring."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_foundry.utils.markdown import split_frontmatter_for_rewrite

SCHEMA_VERSION = 1
CURSOR_CLI_STATE_DIRNAME = "cursor-cli"
SENTINEL_NAME = ".agent-foundry-cursor-cli.json"
FRONTMATTER_PLUGIN_KEY = "x-agent-foundry-plugin"


def cursor_cli_state_dir(project_root: Path | None = None) -> Path:
    if project_root is None:
        return Path.home() / ".agent-foundry" / CURSOR_CLI_STATE_DIRNAME
    return project_root.resolve() / ".agent-foundry" / CURSOR_CLI_STATE_DIRNAME


def state_path_for(plugin_id: str, project_root: Path | None = None) -> Path:
    return cursor_cli_state_dir(project_root) / f"{plugin_id}.json"


def load_state(plugin_id: str, project_root: Path | None = None) -> dict[str, Any] | None:
    path = state_path_for(plugin_id, project_root)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def write_state(
    plugin_id: str,
    *,
    skills: list[str],
    agents: list[str],
    project_root: Path | None = None,
) -> None:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "plugin_id": plugin_id,
        "skills": sorted(set(skills)),
        "agents": sorted(set(agents)),
    }
    sp = state_path_for(plugin_id, project_root)
    sp.parent.mkdir(parents=True, exist_ok=True)
    sp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_skill_sentinel(dest_skill_dir: Path, plugin_id: str) -> None:
    sent = dest_skill_dir / SENTINEL_NAME
    sent.write_text(
        json.dumps({"plugin_id": plugin_id, "kind": "skill"}, indent=2) + "\n",
        encoding="utf-8",
    )


def read_sentinel_skill_plugin(dest: Path) -> str | None:
    sent = dest / SENTINEL_NAME
    if not sent.is_file():
        return None
    try:
        data = json.loads(sent.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict):
        pid = data.get("plugin_id")
        return str(pid) if isinstance(pid, str) else None
    return None


def skill_install_allowed(plugin_id: str, dest: Path, old_state_paths: set[str]) -> bool:
    key = str(dest.resolve())
    if key in old_state_paths:
        return True
    pid = read_sentinel_skill_plugin(dest)
    return pid == plugin_id


def agent_managed_by_plugin(plugin_id: str, dest: Path) -> bool:
    if not dest.is_file():
        return False
    fm, _ = split_frontmatter_for_rewrite(dest.read_text(encoding="utf-8"))
    return fm.get(FRONTMATTER_PLUGIN_KEY) == plugin_id


def agent_install_allowed(plugin_id: str, dest: Path, old_state_paths: set[str]) -> bool:
    key = str(dest.resolve())
    if key in old_state_paths:
        return True
    return agent_managed_by_plugin(plugin_id, dest)
