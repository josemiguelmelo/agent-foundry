"""Small JSON helpers to avoid duplicated read-parse-write patterns."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json_dict(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return raw if isinstance(raw, dict) else None


def read_json_dict_or_default(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    data = read_json_dict(path)
    return default if data is None else data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def ensure_plugins_list(container: dict[str, Any], key: str = "plugins") -> list[Any]:
    items = container.get(key)
    if not isinstance(items, list):
        items = []
        container[key] = items
    return items


def upsert_dict_in_list_by_key(
    items: list[Any],
    *,
    key: str,
    value: str,
    replacement: dict[str, Any],
) -> None:
    for i, item in enumerate(items):
        if isinstance(item, dict) and item.get(key) == value:
            items[i] = replacement
            return
    items.append(replacement)


def remove_dicts_from_list_by_key(
    items: list[Any],
    *,
    key: str,
    value: str,
) -> tuple[list[Any], int]:
    """Return ``(new_list, removed_count)``."""
    new_list = [x for x in items if not (isinstance(x, dict) and x.get(key) == value)]
    return new_list, len(items) - len(new_list)


def read_json_dict_strict(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"Missing JSON file {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in {path}: {e}") from e
    if not isinstance(raw, dict):
        raise RuntimeError(f"Expected JSON object in {path}")
    return raw
