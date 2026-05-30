"""Install/uninstall one specific plugin artifact via provider installers."""

from __future__ import annotations

import json
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from agent_foundry.installers.cursor_cli.manifest import (
    load_cursor_plugin_manifest,
    manifest_path_values,
    resolve_from_plugin_root,
)
from agent_foundry.installers.cursor_cli.rewrite import (
    iter_agent_sources,
    iter_skill_package_dirs,
)
from agent_foundry.installers.selection import (
    SpecificSelection,
    normalize_kind,
    split_scoped_identifier,
)
from agent_foundry.registry import find_registry_file, list_registry_plugins, repository_root

# Re-export for existing imports.
__all__ = ["SpecificSelection", "materialized_specific_plugin", "resolve_specific_selection"]


def _select_skill_matches(plugin_root: Path, identifier: str) -> list[tuple[Path, str]]:
    manifest = load_cursor_plugin_manifest(plugin_root)
    roots = manifest_path_values(manifest.get("skills"))
    out: list[tuple[Path, str]] = []
    needle = identifier.strip().lower()
    for rel in roots:
        for pkg in iter_skill_package_dirs(resolve_from_plugin_root(plugin_root, rel)):
            if pkg.name.lower() == needle:
                out.append((pkg, pkg.name))
    return out


def _select_agent_matches(plugin_root: Path, identifier: str) -> list[tuple[Path, str]]:
    manifest = load_cursor_plugin_manifest(plugin_root)
    roots = manifest_path_values(manifest.get("agents"))
    out: list[tuple[Path, str]] = []
    needle = identifier.strip().lower()
    for rel in roots:
        for src in iter_agent_sources(resolve_from_plugin_root(plugin_root, rel)):
            if src.stem.lower() == needle or src.name.lower() == needle:
                out.append((src, src.stem))
    return out


def _select_mcp_config_matches(
    plugin_root: Path, identifier: str
) -> list[tuple[Path, str]]:
    manifest = load_cursor_plugin_manifest(plugin_root)
    roots = manifest_path_values(manifest.get("mcpServers"))
    out: list[tuple[Path, str]] = []
    needle = identifier.strip().lower()
    for rel in roots:
        mcp_path = resolve_from_plugin_root(plugin_root, rel)
        if not mcp_path.is_file():
            continue
        try:
            data = json.loads(mcp_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid mcp config JSON {mcp_path}: {e}") from e
        servers = data.get("mcpServers")
        if not isinstance(servers, dict):
            continue
        for server_id in servers:
            if str(server_id).lower() == needle:
                out.append((mcp_path, str(server_id)))
    return out


def resolve_specific_selection(kind: str, identifier: str) -> SpecificSelection:
    from agent_foundry.registry.external import (
        is_external_layout_active,
        resolve_external_specific_selection,
        repository_root_from_env,
    )

    if is_external_layout_active():
        return resolve_external_specific_selection(
            repository_root_from_env(), kind, identifier
        )

    normalized_kind = normalize_kind(kind)
    scoped_plugin, scoped_identifier = split_scoped_identifier(identifier)
    matches: list[SpecificSelection] = []

    repo_root = repository_root(find_registry_file())
    for plugin in list_registry_plugins():
        if scoped_plugin and plugin.id != scoped_plugin:
            continue
        plugin_root = plugin.resolved_path(repo_root)
        if normalized_kind == "skill":
            found = _select_skill_matches(plugin_root, scoped_identifier)
        elif normalized_kind == "agent":
            found = _select_agent_matches(plugin_root, scoped_identifier)
        else:
            found = _select_mcp_config_matches(plugin_root, scoped_identifier)
        for source_path, resolved_identifier in found:
            matches.append(
                SpecificSelection(
                    kind=normalized_kind,
                    source_plugin_id=plugin.id,
                    source_path=source_path,
                    resolved_identifier=resolved_identifier,
                )
            )

    if not matches:
        raise RuntimeError(
            f"No {normalized_kind} found for identifier {identifier!r}. "
            "Tip: use '<plugin_id>:<identifier>' if the identifier is ambiguous."
        )
    if len(matches) > 1:
        choices = ", ".join(
            sorted(
                {
                    f"{m.source_plugin_id}:{m.resolved_identifier}"
                    for m in matches
                }
            )
        )
        raise RuntimeError(
            f"Identifier {identifier!r} is ambiguous for kind {normalized_kind!r}. "
            f"Choose one of: {choices}"
        )
    return matches[0]


@contextmanager
def materialized_specific_plugin(selection: SpecificSelection) -> Iterator[Path]:
    with tempfile.TemporaryDirectory(prefix="agent-foundry-specific-") as tmpdir:
        root = Path(tmpdir) / selection.synthetic_plugin_id
        root.mkdir(parents=True, exist_ok=True)

        manifest: dict[str, object] = {
            "name": selection.synthetic_plugin_id,
            "version": "0.0.0",
            "description": (
                f"Generated one-item plugin: {selection.kind} "
                f"{selection.source_plugin_id}:{selection.resolved_identifier}"
            ),
        }

        if selection.kind == "skill":
            target = root / "skills" / selection.resolved_identifier
            shutil.copytree(selection.source_path, target, symlinks=True)
            manifest["skills"] = "./skills"
            manifest["agents"] = []
        elif selection.kind == "agent":
            target = root / "agents" / selection.source_path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(selection.source_path, target)
            manifest["agents"] = [f"./agents/{selection.source_path.name}"]
            manifest["skills"] = []
        else:
            data = json.loads(selection.source_path.read_text(encoding="utf-8"))
            servers = data.get("mcpServers")
            if not isinstance(servers, dict):
                raise RuntimeError(
                    f"Invalid mcp config file (missing mcpServers object): {selection.source_path}"
                )
            one_server = servers.get(selection.resolved_identifier)
            if one_server is None:
                raise RuntimeError(
                    f"MCP server {selection.resolved_identifier!r} not found in {selection.source_path}"
                )
            mcp_file = root / ".mcp.json"
            mcp_file.write_text(
                json.dumps(
                    {"mcpServers": {selection.resolved_identifier: one_server}},
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            manifest["mcpServers"] = "./.mcp.json"
            manifest["skills"] = []
            manifest["agents"] = []

        (root / "plugin.json").write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )
        yield root
