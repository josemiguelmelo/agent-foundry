"""CLI ``--path`` overrides for manifest source roots (skills, agents, etc.)."""

from __future__ import annotations

import json
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from agent_foundry.core.errors import UsageError
from agent_foundry.installers.cursor_cli.manifest import (
    CURSOR_MANIFEST_SUBPATH,
    load_cursor_plugin_manifest,
)
from agent_foundry.utils.paths import resolve_under

_MANIFEST_CANDIDATES: tuple[Path, ...] = (
    CURSOR_MANIFEST_SUBPATH,
    Path(".claude-plugin") / "plugin.json",
    Path("plugin.json"),
)

_KIND_TO_MANIFEST_KEY: dict[str, str] = {
    "skill": "skills",
    "skills": "skills",
    "agent": "agents",
    "agents": "agents",
    "command": "commands",
    "commands": "commands",
    "mcp": "mcpServers",
    "mcp-config": "mcpServers",
    "mcp_config": "mcpServers",
    "mcp-configs": "mcpServers",
    "mcpservers": "mcpServers",
}


def _normalize_kind_token(kind: str) -> str:
    key = _KIND_TO_MANIFEST_KEY.get(kind.strip().lower())
    if not key:
        supported = ", ".join(sorted(set(_KIND_TO_MANIFEST_KEY.keys())))
        raise UsageError(
            f"Unknown --path kind {kind!r}. Supported kinds: {supported}."
        )
    return key


def _normalize_path_value(raw: str, *, plugin_root: Path) -> str:
    resolved = resolve_under(plugin_root, raw.strip())
    try:
        rel = resolved.relative_to(plugin_root.resolve())
        return f"./{rel.as_posix()}"
    except ValueError:
        return str(resolved)


def parse_path_overrides(argv: list[str] | None) -> dict[str, list[str]] | None:
    """Parse repeatable ``KIND:DIR`` values into manifest-keyed override lists."""
    if not argv:
        return None
    out: dict[str, list[str]] = {}
    for item in argv:
        raw = str(item).strip()
        if ":" not in raw:
            raise UsageError(
                f"Invalid --path {raw!r}; expected format '<kind>:<dir>'."
            )
        kind, path = raw.split(":", 1)
        kind = kind.strip()
        path = path.strip()
        if not kind or not path:
            raise UsageError(
                f"Invalid --path {raw!r}; kind and directory must be non-empty."
            )
        manifest_key = _normalize_kind_token(kind)
        out.setdefault(manifest_key, []).append(path)
    return out or None


def apply_source_path_overrides(
    manifest: dict[str, Any],
    overrides: dict[str, list[str]],
    *,
    plugin_root: Path,
) -> dict[str, Any]:
    """Return a shallow copy of ``manifest`` with overridden source path keys."""
    patched = dict(manifest)
    for key, paths in overrides.items():
        normalized = [_normalize_path_value(p, plugin_root=plugin_root) for p in paths]
        if len(normalized) == 1:
            patched[key] = normalized[0]
        else:
            patched[key] = normalized
    return patched


def find_manifest_file(plugin_root: Path) -> Path | None:
    root = plugin_root.resolve()
    for rel in _MANIFEST_CANDIDATES:
        mpath = root / rel
        if mpath.is_file():
            return mpath
    return None


def validate_override_paths(
    plugin_root: Path, overrides: dict[str, list[str]]
) -> None:
    """Ensure each overridden path exists under ``plugin_root``."""
    root = plugin_root.resolve()
    for key, paths in overrides.items():
        for raw in paths:
            target = resolve_under(root, raw)
            if key == "mcpServers":
                if not target.is_file():
                    raise FileNotFoundError(
                        f"--path mcpServers:{raw} does not exist or is not a file: {target}"
                    )
                continue
            if not target.exists():
                raise FileNotFoundError(
                    f"--path {key}:{raw} does not exist under plugin root: {target}"
                )


def write_manifest_file(manifest_path: Path, manifest: dict[str, Any]) -> None:
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )


def load_effective_manifest(
    plugin_root: Path,
    overrides: dict[str, list[str]] | None,
) -> dict[str, Any]:
    """Load plugin manifest and apply optional source path overrides."""
    manifest = load_cursor_plugin_manifest(plugin_root)
    if not overrides:
        return manifest
    return apply_source_path_overrides(
        manifest, overrides, plugin_root=plugin_root.resolve()
    )


def resolve_override_dir(
    base: Path, overrides: dict[str, list[str]] | None, manifest_key: str
) -> Path | None:
    """Return the first overridden directory for ``manifest_key``, or None."""
    if not overrides:
        return None
    paths = overrides.get(manifest_key)
    if not paths:
        return None
    return resolve_under(base.resolve(), paths[0])


@contextmanager
def prepared_plugin_for_install(
    plugin_root: Path,
    overrides: dict[str, list[str]] | None,
) -> Iterator[Path]:
    """
    Yield a plugin root ready for install.

    When ``overrides`` is set, copy ``plugin_root`` to a temp dir, patch the manifest,
    and validate paths on the copy (does not mutate the user's tree).
    """
    root = plugin_root.resolve()
    if not overrides:
        yield root
        return

    validate_override_paths(root, overrides)

    with tempfile.TemporaryDirectory(prefix="agent-foundry-path-override-") as tmpdir:
        dest = Path(tmpdir) / root.name
        shutil.copytree(root, dest, symlinks=True)
        manifest_path = find_manifest_file(dest)
        if manifest_path is None:
            manifest = {
                "name": dest.name,
                "version": "0.0.0",
                "description": f"Generated manifest for {dest.name}",
            }
            manifest_path = dest / "plugin.json"
        else:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if not isinstance(manifest, dict):
                manifest = {}
        patched = apply_source_path_overrides(
            manifest, overrides, plugin_root=dest.resolve()
        )
        write_manifest_file(manifest_path, patched)
        validate_override_paths(dest, overrides)
        yield dest.resolve()
