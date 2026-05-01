"""Cursor plugin manifest helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CURSOR_MANIFEST_SUBPATH = Path(".cursor-plugin") / "plugin.json"


def manifest_path_values(raw: Any) -> list[Path]:
    if isinstance(raw, str) and raw.strip():
        return [Path(raw.strip())]
    if isinstance(raw, list):
        return [Path(str(x).strip()) for x in raw if isinstance(x, str) and str(x).strip()]
    return []


def load_cursor_plugin_manifest(plugin_root: Path) -> dict[str, Any]:
    mpath = plugin_root / CURSOR_MANIFEST_SUBPATH
    if not mpath.is_file():
        raise RuntimeError(
            f"Missing Cursor manifest: {mpath} (expected under plugin root)."
        )
    try:
        data = json.loads(mpath.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid Cursor plugin JSON {mpath}: {e}") from e
    return data if isinstance(data, dict) else {}


def resolve_from_plugin_root(plugin_root: Path, rel: Path) -> Path:
    return (plugin_root / rel).resolve()
