"""Registry discovery and row parsing helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_foundry.registry.document import load_document

REGISTRY_REL = Path("registry") / "plugins.yaml"


@dataclass(frozen=True)
class RegistryPlugin:
    """Normalized row from ``registry/plugins.yaml``."""

    id: str
    path: str
    version: str
    summary: str

    def resolved_path(self, repo_root: Path) -> Path:
        candidate = Path(self.path)
        if not candidate.is_absolute():
            candidate = repo_root / candidate
        return candidate.resolve()


def parse_plugin_row(row: object) -> RegistryPlugin | None:
    if not isinstance(row, dict):
        return None
    plugin_id = row.get("id")
    raw_path = row.get("path")
    if not isinstance(plugin_id, str) or not plugin_id.strip():
        return None
    if not isinstance(raw_path, str) or not raw_path.strip():
        return None
    return RegistryPlugin(
        id=plugin_id.strip(),
        path=raw_path.strip(),
        version=str(row.get("version") or ""),
        summary=str(row.get("summary") or ""),
    )


def find_registry_file() -> Path:
    """Resolve registry/plugins.yaml: env, cwd walk, or package parent."""
    env = os.environ.get("AGENT_FOUNDRY_REPO")
    if env:
        p = Path(env).expanduser().resolve() / REGISTRY_REL
        if p.is_file():
            return p
        raise FileNotFoundError(f"AGENT_FOUNDRY_REPO is set but missing registry: {p}")

    cwd = Path.cwd().resolve()
    for base in [cwd, *cwd.parents]:
        candidate = base / REGISTRY_REL
        if candidate.is_file():
            return candidate

    pkg_dir = Path(__file__).resolve().parent.parent
    candidate = pkg_dir.parent / REGISTRY_REL
    if candidate.is_file():
        return candidate

    raise FileNotFoundError(
        "Could not find registry/plugins.yaml. Run from the agent-foundry repo, "
        "or set AGENT_FOUNDRY_REPO to the repository root."
    )


def repository_root(registry_file: Path) -> Path:
    """Repository root containing ``plugins/`` and ``registry/``."""
    return registry_file.parent.parent.resolve()


def load_registry() -> dict[str, Any]:
    return load_document(find_registry_file())


def list_registry_plugins() -> list[RegistryPlugin]:
    reg_file = find_registry_file()
    rows = load_document(reg_file).get("plugins")
    if not isinstance(rows, list):
        return []
    plugins: list[RegistryPlugin] = []
    for row in rows:
        parsed = parse_plugin_row(row)
        if parsed:
            plugins.append(parsed)
    return plugins


def get_registry_plugin(plugin_id: str) -> RegistryPlugin:
    for entry in list_registry_plugins():
        if entry.id == plugin_id:
            return entry
    raise KeyError(f"Unknown plugin id: {plugin_id!r}")


def resolve_plugin_dir(plugin_id: str) -> Path:
    entry = get_registry_plugin(plugin_id)
    repo_root = repository_root(find_registry_file())
    resolved = entry.resolved_path(repo_root)
    if resolved.is_dir():
        return resolved
    raise FileNotFoundError(f"Plugin {plugin_id!r}: path is not a directory: {resolved}")
