"""Read/write ``registry/plugins.yaml`` as a YAML document."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REGISTRY_HEADER = """# Central registry: list plugins (id → path). Detail lives in each plugin folder.
"""


def load_document(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    return data if isinstance(data, dict) else {}


def plugins_list_mut(data: dict[str, Any]) -> list[Any]:
    """Return ``data['plugins']`` as a list, normalizing missing or wrong type."""
    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        plugins = []
        data["plugins"] = plugins
    return plugins


def save_document(path: Path, data: dict[str, Any]) -> None:
    dumped = yaml.safe_dump(
        data,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    ).rstrip() + "\n"
    path.write_text(REGISTRY_HEADER + "\n" + dumped, encoding="utf-8")
