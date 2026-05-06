"""GitHub Copilot CLI plugin install/uninstall."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any

from agent_foundry.installers.common import which_cmd
from agent_foundry.installers.cursor_cli.manifest import (
    load_cursor_plugin_manifest,
    manifest_path_values,
    resolve_from_plugin_root,
)
from agent_foundry.installers.cursor_cli.rewrite import (
    iter_agent_sources,
    iter_skill_package_dirs,
)
from agent_foundry.utils.command_runner import run_command
from agent_foundry.utils.fsutil import prune_empty_parents, unlink_or_rmtree

_STATE_DIRNAME = "copilot"
_SKILL_SENTINEL_NAME = ".agent-foundry-copilot.json"


def _state_dir(project_root: Path | None = None) -> Path:
    if project_root is None:
        return Path.home() / ".agent-foundry" / _STATE_DIRNAME
    return project_root.resolve() / ".agent-foundry" / _STATE_DIRNAME


def _state_path(plugin_id: str, project_root: Path | None = None) -> Path:
    return _state_dir(project_root) / f"{plugin_id}.json"


def _load_state(plugin_id: str, project_root: Path | None = None) -> dict[str, Any] | None:
    sp = _state_path(plugin_id, project_root)
    if not sp.is_file():
        return None
    try:
        data = json.loads(sp.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _write_state(
    plugin_id: str,
    *,
    project_root: Path | None,
    skills: list[str],
    agents: list[str],
    commands: list[str],
) -> None:
    payload = {
        "plugin_id": plugin_id,
        "skills": sorted(set(skills)),
        "agents": sorted(set(agents)),
        "commands": sorted(set(commands)),
    }
    sp = _state_path(plugin_id, project_root)
    sp.parent.mkdir(parents=True, exist_ok=True)
    sp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _managed_skill(dest: Path, plugin_id: str) -> bool:
    sent = dest / _SKILL_SENTINEL_NAME
    if not sent.is_file():
        return False
    try:
        data = json.loads(sent.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return isinstance(data, dict) and data.get("plugin_id") == plugin_id


def _install_copilot_project_mirror(plugin_id: str, plugin_root: Path) -> None:
    root = Path.cwd().resolve()
    manifest = load_cursor_plugin_manifest(plugin_root)
    skill_roots = manifest_path_values(manifest.get("skills"))
    agent_roots = manifest_path_values(manifest.get("agents"))
    command_roots = manifest_path_values(manifest.get("commands"))

    skills_base = root / ".github" / "skills"
    agents_base = root / ".github" / "agents"
    commands_base = root / ".claude" / "commands"
    skills_base.mkdir(parents=True, exist_ok=True)
    agents_base.mkdir(parents=True, exist_ok=True)
    commands_base.mkdir(parents=True, exist_ok=True)

    old_state = _load_state(plugin_id, root) or {}
    old_skills = {str((root / p).resolve()) for p in old_state.get("skills") or []}
    old_agents = {str((root / p).resolve()) for p in old_state.get("agents") or []}
    old_commands = {str((root / p).resolve()) for p in old_state.get("commands") or []}

    recorded_skills: list[str] = []
    recorded_agents: list[str] = []
    recorded_commands: list[str] = []

    for rel in skill_roots:
        skills_src = resolve_from_plugin_root(plugin_root, rel)
        for pkg in iter_skill_package_dirs(skills_src):
            dest = skills_base / pkg.name
            dest_key = str(dest.resolve())
            if dest.exists() or dest.is_symlink():
                if dest_key not in old_skills and not _managed_skill(dest, plugin_id):
                    raise RuntimeError(
                        f"Copilot: refusing to overwrite project skill {dest} (not managed by plugin {plugin_id!r})."
                    )
                unlink_or_rmtree(dest)
            shutil.copytree(pkg, dest, symlinks=True)
            (dest / _SKILL_SENTINEL_NAME).write_text(
                json.dumps({"plugin_id": plugin_id, "kind": "skill"}, indent=2) + "\n",
                encoding="utf-8",
            )
            recorded_skills.append(str(dest.resolve().relative_to(root)))

    for rel in agent_roots:
        agents_src = resolve_from_plugin_root(plugin_root, rel)
        for src in iter_agent_sources(agents_src):
            dest = agents_base / src.name
            dest_key = str(dest.resolve())
            if dest.exists() or dest.is_symlink():
                if dest_key not in old_agents:
                    raise RuntimeError(
                        f"Copilot: refusing to overwrite project agent {dest} (not managed by plugin {plugin_id!r})."
                    )
                unlink_or_rmtree(dest)
            dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            recorded_agents.append(str(dest.resolve().relative_to(root)))

    for rel in command_roots:
        commands_src = resolve_from_plugin_root(plugin_root, rel)
        if not commands_src.exists():
            continue
        if commands_src.is_file():
            dest = commands_base / commands_src.name
            dest_key = str(dest.resolve())
            if dest.exists() or dest.is_symlink():
                if dest_key not in old_commands:
                    raise RuntimeError(
                        f"Copilot: refusing to overwrite project command {dest} (not managed by plugin {plugin_id!r})."
                    )
                unlink_or_rmtree(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(commands_src, dest)
            recorded_commands.append(str(dest.resolve().relative_to(root)))
            continue

        for item in sorted(commands_src.iterdir()):
            dest = commands_base / item.name
            dest_key = str(dest.resolve())
            if dest.exists() or dest.is_symlink():
                if dest_key not in old_commands:
                    raise RuntimeError(
                        f"Copilot: refusing to overwrite project command path {dest} (not managed by plugin {plugin_id!r})."
                    )
                unlink_or_rmtree(dest)
            if item.is_dir():
                shutil.copytree(item, dest, symlinks=True)
            else:
                shutil.copy2(item, dest)
            recorded_commands.append(str(dest.resolve().relative_to(root)))

    if not recorded_skills and not recorded_agents and not recorded_commands:
        raise RuntimeError(
            "Copilot: nothing to install in project scope — declare skills/agents/commands in plugin.json."
        )

    _write_state(
        plugin_id,
        project_root=root,
        skills=recorded_skills,
        agents=recorded_agents,
        commands=recorded_commands,
    )
    print(
        "Copilot (project): installed "
        f"{len(recorded_skills)} skill dir(s), {len(recorded_agents)} agent file(s), "
        f"{len(recorded_commands)} command path(s).",
        file=sys.stderr,
    )


def install_copilot(plugin_id: str, plugin_root: Path, *, in_project: bool = False) -> None:
    """GitHub Copilot CLI: `copilot plugin install <path>`."""
    if in_project:
        _install_copilot_project_mirror(plugin_id, plugin_root)
        return
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
        root = Path.cwd().resolve()
        state = _load_state(plugin_id, root)
        sp = _state_path(plugin_id, root)
        if not state:
            print(
                f"Copilot (project): no install record for plugin {plugin_id!r} ({sp}).",
                file=sys.stderr,
            )
            return
        for rel in state.get("skills") or []:
            unlink_or_rmtree((root / rel).resolve())
        for rel in state.get("agents") or []:
            unlink_or_rmtree((root / rel).resolve())
        for rel in state.get("commands") or []:
            unlink_or_rmtree((root / rel).resolve())
        if sp.is_file():
            sp.unlink()
        prune_empty_parents(root / ".github" / "skills", stop_at=root)
        prune_empty_parents(root / ".github" / "agents", stop_at=root)
        prune_empty_parents(root / ".claude" / "commands", stop_at=root)
        prune_empty_parents(_state_dir(root), stop_at=root)
        print("Copilot (project): uninstall completed.", file=sys.stderr)
        return

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
