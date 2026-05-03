"""Cursor CLI install/uninstall workflow."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from agent_foundry.utils.fsutil import prune_empty_parents, unlink_or_rmtree
from agent_foundry.utils.paths import install_base as cli_install_base

from .manifest import (
    load_cursor_plugin_manifest,
    manifest_path_values,
    resolve_from_plugin_root,
)
from .rewrite import iter_agent_sources, iter_skill_package_dirs, rewrite_agent_for_cli
from .state import (
    agent_collision_detail,
    agent_install_allowed,
    agent_managed_by_plugin,
    cursor_cli_state_dir,
    load_state,
    skill_install_allowed,
    state_path_for,
    write_skill_sentinel,
    write_state,
)


def install_cursor_cli(
    plugin_id: str,
    plugin_root: Path,
    *,
    in_project: bool = False,
    force: bool = False,
) -> None:
    """Mirror skills/agents into Cursor CLI discovery paths (global ``~/.cursor/`` or project ``./.cursor/``)."""
    state_anchor = Path.cwd().resolve() if in_project else None
    manifest = load_cursor_plugin_manifest(plugin_root)
    skill_roots = manifest_path_values(manifest.get("skills"))
    agent_roots = manifest_path_values(manifest.get("agents"))

    old = load_state(plugin_id, state_anchor) or {}
    old_skills: set[str] = set(old.get("skills") or [])
    old_agents: set[str] = set(old.get("agents") or [])
    if isinstance(old.get("skills"), list):
        old_skills = {str(x) for x in old["skills"]}
    if isinstance(old.get("agents"), list):
        old_agents = {str(x) for x in old["agents"]}

    base = cli_install_base(in_project=in_project)
    cursor_skills = base / ".cursor" / "skills"
    cursor_agents = base / ".cursor" / "agents"
    cursor_skills.mkdir(parents=True, exist_ok=True)
    cursor_agents.mkdir(parents=True, exist_ok=True)

    recorded_skills: list[str] = []
    recorded_agents: list[str] = []

    for rel in skill_roots:
        skills_src = resolve_from_plugin_root(plugin_root, rel)
        if not skills_src.exists():
            print(
                f"Cursor CLI: skills path does not exist, skipping: {skills_src}",
                file=sys.stderr,
            )
            continue
        packages = iter_skill_package_dirs(skills_src)
        if not packages:
            print(
                f"Cursor CLI: skipping skills path {skills_src} (no SKILL.md packages).",
                file=sys.stderr,
            )
            continue
        for pkg in packages:
            folder_name = pkg.name
            dest = cursor_skills / folder_name
            dest_abs = dest.resolve()
            dest_key = str(dest_abs)
            if dest.exists() or dest.is_symlink():
                if not skill_install_allowed(plugin_id, dest, old_skills):
                    raise RuntimeError(
                        "Cursor CLI: refusing to overwrite existing skill "
                        f"{folder_name!r} at {dest} (not managed by "
                        f"agent-foundry cursor-cli for plugin {plugin_id!r}). "
                        "Remove it or install under a different profile."
                    )
                unlink_or_rmtree(dest)
            shutil.copytree(pkg, dest, symlinks=True)
            write_skill_sentinel(dest, plugin_id)
            recorded_skills.append(dest_key)

    for rel in agent_roots:
        agents_src = resolve_from_plugin_root(plugin_root, rel)
        if not agents_src.exists():
            print(
                f"Cursor CLI: agents path does not exist, skipping: {agents_src}",
                file=sys.stderr,
            )
            continue
        sources = iter_agent_sources(agents_src)
        if not sources:
            print(
                f"Cursor CLI: skipping agents path {agents_src} (no *.md agent files).",
                file=sys.stderr,
            )
            continue

        for src in sources:
            dest_name = f"{src.stem}.md"
            dest = cursor_agents / dest_name
            dest_key = str(dest.resolve())
            if dest.exists() or dest.is_symlink():
                allowed = agent_install_allowed(plugin_id, dest, old_agents)
                if not allowed and not force:
                    detail = agent_collision_detail(dest)
                    raise RuntimeError(
                        "Cursor CLI: refusing to overwrite existing agent "
                        f"{dest_name!r} at {dest} ({detail}). "
                        "Re-run with --force to replace it."
                    )
                unlink_or_rmtree(dest)
            dest.write_text(rewrite_agent_for_cli(plugin_id, src), encoding="utf-8")
            recorded_agents.append(dest_key)

    recorded_paths = {str(Path(p).resolve()) for p in recorded_agents}
    for old_key in old_agents:
        if old_key in recorded_paths:
            continue
        legacy = Path(old_key)
        if legacy.is_file() and agent_managed_by_plugin(plugin_id, legacy):
            unlink_or_rmtree(legacy)

    if not recorded_skills and not recorded_agents:
        raise RuntimeError(
            "Cursor CLI: nothing to install — add at least one skill package or "
            f"agent `.md` under the `skills` / `agents` paths declared in the plugin "
            f"manifest under {plugin_root.resolve()}."
        )

    write_state(
        plugin_id,
        skills=recorded_skills,
        agents=recorded_agents,
        project_root=state_anchor,
    )

    scope_hint = str(base / ".cursor") if in_project else "~/.cursor"
    print(
        f"Cursor CLI: installed {len(recorded_skills)} skill dir(s), "
        f"{len(recorded_agents)} agent file(s) under {scope_hint}/",
        file=sys.stderr,
    )
    print(
        "Restart `cursor-agent` / open a new CLI session if skills do not appear.",
        file=sys.stderr,
    )


def uninstall_cursor_cli(plugin_id: str, *, in_project: bool = False) -> None:
    state_anchor = Path.cwd().resolve() if in_project else None
    state = load_state(plugin_id, state_anchor)
    sp = state_path_for(plugin_id, state_anchor)
    if not state:
        print(
            f"Cursor CLI: no install record for plugin {plugin_id!r} ({sp}).",
            file=sys.stderr,
        )
        return

    for p in state.get("skills") or []:
        target = Path(str(p))
        if unlink_or_rmtree(target):
            print(f"Cursor CLI: removed skill dir {target}", file=sys.stderr)

    for p in state.get("agents") or []:
        target = Path(str(p))
        if unlink_or_rmtree(target):
            print(f"Cursor CLI: removed agent file {target}", file=sys.stderr)

    if sp.is_file():
        sp.unlink()
    print(f"Cursor CLI: removed state {sp}", file=sys.stderr)

    base = cli_install_base(in_project=in_project)
    prune_empty_parents(base / ".cursor" / "skills", stop_at=base)
    prune_empty_parents(base / ".cursor" / "agents", stop_at=base)
    prune_empty_parents(sp.parent, stop_at=base)
    prune_empty_parents(cursor_cli_state_dir(state_anchor), stop_at=base)
