"""Convention-based layout resolution for external git repositories."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from agent_foundry.installers.cursor_cli.manifest import CURSOR_MANIFEST_SUBPATH
from agent_foundry.installers.cursor_cli.rewrite import iter_agent_sources, iter_skill_package_dirs
from agent_foundry.installers.selection import (
    SpecificSelection,
    normalize_kind,
    split_scoped_identifier,
)
_REGISTRY_REL = Path("registry") / "plugins.yaml"

LAYOUT_ENV = "AGENT_FOUNDRY_LAYOUT"
LAYOUT_EXTERNAL = "external"
LAYOUT_REGISTRY = "registry"

_GIT_URL_PREFIXES = ("https://", "http://", "git@", "ssh://", "git://")
_GIT_URL_SUFFIX = ".git"


def is_git_remote_url(value: str) -> bool:
    """Return True when ``value`` looks like a git remote URL, not a local path."""
    raw = value.strip()
    if not raw:
        return False
    candidate = Path(raw).expanduser()
    if candidate.exists():
        return False
    lowered = raw.lower()
    if lowered.startswith(_GIT_URL_PREFIXES):
        return True
    if lowered.endswith(_GIT_URL_SUFFIX):
        return True
    if re.match(r"^[^@\s]+@[^@\s]+:[^\s]+$", raw):
        return True
    return False


def shallow_clone_repo(url: str, *, dest: Path) -> Path:
    """Shallow-clone ``url`` into ``dest`` and return the clone root."""
    import shutil as _shutil

    git_bin = _shutil.which("git")
    if not git_bin:
        raise RuntimeError("git is required to clone a remote repository but was not found on PATH.")
    dest.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [git_bin, "clone", "--depth", "1", url.strip(), str(dest)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        raise RuntimeError(
            f"Failed to clone repository {url!r}: {stderr or 'unknown git error'}"
        )
    return dest.resolve()


def is_registry_repo(root: Path) -> bool:
    return (root.resolve() / _REGISTRY_REL).is_file()


def is_external_repo(root: Path) -> bool:
    base = root.resolve()
    for name in ("agents", "skills", "plugins"):
        child = base / name
        if child.is_dir():
            return True
    return False


def repository_root_from_env() -> Path:
    env = os.environ.get("AGENT_FOUNDRY_REPO")
    if not env:
        raise FileNotFoundError(
            "AGENT_FOUNDRY_REPO is not set. Run inside an install repo context."
        )
    return Path(env).expanduser().resolve()


def is_external_layout_active() -> bool:
    return os.environ.get(LAYOUT_ENV) == LAYOUT_EXTERNAL


def resolve_external_plugin_dir(repo_root: Path, plugin_id: str) -> Path:
    plugin_root = repo_root.resolve() / "plugins" / plugin_id
    if not plugin_root.is_dir():
        raise FileNotFoundError(
            f"Plugin {plugin_id!r} not found under plugins/: {plugin_root}"
        )
    return plugin_root


def _has_plugin_manifest(plugin_root: Path) -> bool:
    root = plugin_root.resolve()
    candidates = (
        CURSOR_MANIFEST_SUBPATH,
        Path(".claude-plugin") / "plugin.json",
        Path("plugin.json"),
    )
    return any((root / rel).is_file() for rel in candidates)


def _write_minimal_manifest(plugin_root: Path) -> None:
    manifest: dict[str, object] = {
        "name": plugin_root.name,
        "version": "0.0.0",
        "description": f"Generated manifest for external plugin {plugin_root.name}",
    }
    skills_dir = plugin_root / "skills"
    agents_dir = plugin_root / "agents"
    if skills_dir.is_dir():
        manifest["skills"] = "./skills"
    else:
        manifest["skills"] = []
    if agents_dir.is_dir():
        agent_files = sorted(agents_dir.glob("*.md"))
        if agent_files:
            manifest["agents"] = [f"./agents/{p.name}" for p in agent_files]
        else:
            manifest["agents"] = "./agents"
    else:
        manifest["agents"] = []
    (plugin_root / "plugin.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )


@contextmanager
def prepared_external_plugin_root(plugin_root: Path) -> Iterator[Path]:
    """Yield a plugin root that has a manifest (materialized copy when needed)."""
    root = plugin_root.resolve()
    if _has_plugin_manifest(root):
        yield root
        return
    with tempfile.TemporaryDirectory(prefix="agent-foundry-external-plugin-") as tmpdir:
        dest = Path(tmpdir) / root.name
        shutil.copytree(root, dest, symlinks=True)
        _write_minimal_manifest(dest)
        yield dest


def _agent_file_matches(path: Path, identifier: str) -> bool:
    needle = identifier.strip().lower()
    if not path.is_file() or path.suffix.lower() != ".md":
        return False
    return path.stem.lower() == needle or path.name.lower() == needle


def _collect_root_skill_matches(
    repo_root: Path, identifier: str
) -> list[tuple[Path, str, str]]:
    """Return (source_path, resolved_id, source_plugin_id) for repo-root skills/."""
    out: list[tuple[Path, str, str]] = []
    skills_root = repo_root / "skills"
    if not skills_root.is_dir():
        return out
    for pkg in iter_skill_package_dirs(skills_root):
        if pkg.name.lower() == identifier.strip().lower():
            out.append((pkg, pkg.name, "external"))
    return out


def _collect_root_agent_matches(
    repo_root: Path, identifier: str
) -> list[tuple[Path, str, str]]:
    out: list[tuple[Path, str, str]] = []
    agents_root = repo_root / "agents"
    if not agents_root.is_dir():
        return out
    for src in iter_agent_sources(agents_root):
        if _agent_file_matches(src, identifier):
            out.append((src, src.stem, "external"))
    return out


def _collect_plugin_skill_matches(
    plugin_root: Path, plugin_id: str, identifier: str
) -> list[tuple[Path, str, str]]:
    out: list[tuple[Path, str, str]] = []
    skills_root = plugin_root / "skills"
    if not skills_root.is_dir():
        return out
    for pkg in iter_skill_package_dirs(skills_root):
        if pkg.name.lower() == identifier.strip().lower():
            out.append((pkg, pkg.name, plugin_id))
    return out


def _collect_plugin_agent_matches(
    plugin_root: Path, plugin_id: str, identifier: str
) -> list[tuple[Path, str, str]]:
    out: list[tuple[Path, str, str]] = []
    agents_root = plugin_root / "agents"
    if not agents_root.is_dir():
        return out
    for src in iter_agent_sources(agents_root):
        if _agent_file_matches(src, identifier):
            out.append((src, src.stem, plugin_id))
    return out


def _iter_plugin_dirs(repo_root: Path) -> list[tuple[str, Path]]:
    plugins_root = repo_root / "plugins"
    if not plugins_root.is_dir():
        return []
    return [
        (child.name, child)
        for child in sorted(plugins_root.iterdir())
        if child.is_dir()
    ]


def resolve_external_specific_selection(
    repo_root: Path, kind: str, identifier: str
) -> SpecificSelection:
    normalized_kind = normalize_kind(kind)
    if normalized_kind == "mcp_config":
        raise RuntimeError(
            "MCP config install is not supported from external repository layout."
        )

    scoped_plugin, scoped_identifier = split_scoped_identifier(identifier)
    repo_root = repo_root.resolve()
    raw_matches: list[tuple[Path, str, str]] = []

    if scoped_plugin:
        plugin_root = repo_root / "plugins" / scoped_plugin
        if not plugin_root.is_dir():
            raise RuntimeError(
                f"Plugin {scoped_plugin!r} not found under plugins/ in external repository."
            )
        if normalized_kind == "skill":
            raw_matches = _collect_plugin_skill_matches(
                plugin_root, scoped_plugin, scoped_identifier
            )
        else:
            raw_matches = _collect_plugin_agent_matches(
                plugin_root, scoped_plugin, scoped_identifier
            )
    else:
        if normalized_kind == "skill":
            raw_matches.extend(
                _collect_root_skill_matches(repo_root, scoped_identifier)
            )
            for plugin_id, plugin_root in _iter_plugin_dirs(repo_root):
                raw_matches.extend(
                    _collect_plugin_skill_matches(
                        plugin_root, plugin_id, scoped_identifier
                    )
                )
        else:
            raw_matches.extend(
                _collect_root_agent_matches(repo_root, scoped_identifier)
            )
            for plugin_id, plugin_root in _iter_plugin_dirs(repo_root):
                raw_matches.extend(
                    _collect_plugin_agent_matches(
                        plugin_root, plugin_id, scoped_identifier
                    )
                )

    matches = [
        SpecificSelection(
            kind=normalized_kind,
            source_plugin_id=source_plugin_id,
            source_path=source_path,
            resolved_identifier=resolved_id,
        )
        for source_path, resolved_id, source_plugin_id in raw_matches
    ]

    if not matches:
        raise RuntimeError(
            f"No {normalized_kind} found for identifier {identifier!r} in external repository. "
            "Tip: use '<plugin_id>:<identifier>' when the item lives under plugins/."
        )
    if len(matches) > 1:
        choices = ", ".join(
            sorted(
                {f"{m.source_plugin_id}:{m.resolved_identifier}" for m in matches}
            )
        )
        raise RuntimeError(
            f"Identifier {identifier!r} is ambiguous for kind {normalized_kind!r}. "
            f"Choose one of: {choices}"
        )
    return matches[0]
