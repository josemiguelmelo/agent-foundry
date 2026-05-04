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
_AGENT_FOUNDRY_DIRNAME = ".agent-foundry"
_AGENT_FOUNDRY_GITIGNORE = (
    "# Local agent-foundry data (not portable)\n"
    "memory/\n"
)


def cursor_cli_state_dir(project_root: Path | None = None) -> Path:
    if project_root is None:
        return Path.home() / _AGENT_FOUNDRY_DIRNAME / CURSOR_CLI_STATE_DIRNAME
    return project_root.resolve() / _AGENT_FOUNDRY_DIRNAME / CURSOR_CLI_STATE_DIRNAME


def state_path_for(plugin_id: str, project_root: Path | None = None) -> Path:
    return cursor_cli_state_dir(project_root) / f"{plugin_id}.json"


def resolve_state_path(path_str: str, project_root: Path | None) -> str:
    """Resolve a path from install state (relative to project or absolute)."""
    path = Path(path_str)
    if project_root is not None and not path.is_absolute():
        return str((project_root.resolve() / path).resolve())
    return str(path.expanduser().resolve())


def ensure_agent_foundry_gitignore(project_root: Path) -> None:
    """Ensure ``.agent-foundry/.gitignore`` ignores local data such as ``memory/``."""
    root = project_root.resolve()
    agent_foundry = root / _AGENT_FOUNDRY_DIRNAME
    agent_foundry.mkdir(parents=True, exist_ok=True)
    gitignore = agent_foundry / ".gitignore"
    if not gitignore.is_file():
        gitignore.write_text(_AGENT_FOUNDRY_GITIGNORE, encoding="utf-8")
        return
    text = gitignore.read_text(encoding="utf-8")
    if "memory/" in text:
        return
    sep = "" if text.endswith("\n") else "\n"
    gitignore.write_text(f"{text}{sep}memory/\n", encoding="utf-8")


def _paths_for_project_state_json(paths: list[str], project_root: Path) -> list[str]:
    root = project_root.resolve()
    out: list[str] = []
    for p in paths:
        ap = Path(p).resolve()
        try:
            out.append(ap.relative_to(root).as_posix())
        except ValueError:
            out.append(str(ap))
    return sorted(set(out))


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
    if project_root is not None:
        root = project_root.resolve()
        skill_paths = _paths_for_project_state_json(skills, root)
        agent_paths = _paths_for_project_state_json(agents, root)
        ensure_agent_foundry_gitignore(root)
    else:
        skill_paths = sorted(set(skills))
        agent_paths = sorted(set(agents))
    payload = {
        "schema_version": SCHEMA_VERSION,
        "plugin_id": plugin_id,
        "skills": skill_paths,
        "agents": agent_paths,
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


def agent_collision_detail(dest: Path) -> str:
    """Explain why ``dest`` cannot be overwritten without ``--force``."""
    if dest.is_symlink():
        return "path is a symlink"
    if not dest.is_file():
        return "path exists but is not a regular agent file"
    fm, _ = split_frontmatter_for_rewrite(dest.read_text(encoding="utf-8"))
    pid = fm.get(FRONTMATTER_PLUGIN_KEY)
    if isinstance(pid, str) and pid.strip():
        return f"owned by cursor-cli plugin {pid!r}"
    return "no agent-foundry ownership marker (manual file or other tool)"
