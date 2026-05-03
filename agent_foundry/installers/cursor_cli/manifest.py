"""Cursor plugin manifest helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CURSOR_MANIFEST_SUBPATH = Path(".cursor-plugin") / "plugin.json"

# When installing from a shallow clone or an older registry snapshot, the Cursor-specific
# manifest may be absent even though Claude/root manifests list the same skill paths.
_MANIFEST_CANDIDATES: tuple[Path, ...] = (
    CURSOR_MANIFEST_SUBPATH,
    Path(".claude-plugin") / "plugin.json",
    Path("plugin.json"),
)


def manifest_path_values(raw: Any) -> list[Path]:
    if isinstance(raw, str) and raw.strip():
        return [Path(raw.strip())]
    if isinstance(raw, list):
        return [Path(str(x).strip()) for x in raw if isinstance(x, str) and str(x).strip()]
    return []


def load_cursor_plugin_manifest(plugin_root: Path) -> dict[str, Any]:
    root = plugin_root.resolve()
    tried: list[Path] = []
    for rel in _MANIFEST_CANDIDATES:
        mpath = root / rel
        tried.append(mpath)
        if not mpath.is_file():
            continue
        try:
            data = json.loads(mpath.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid plugin JSON {mpath}: {e}") from e
        return data if isinstance(data, dict) else {}
    raise RuntimeError(
        "Missing plugin manifest for Cursor CLI install; tried:\n  "
        + "\n  ".join(str(p) for p in tried)
        + "\nAt least one of these JSON files must exist under the plugin root."
    )


def resolve_from_plugin_root(plugin_root: Path, rel: Path) -> Path:
    return (plugin_root / rel).resolve()
