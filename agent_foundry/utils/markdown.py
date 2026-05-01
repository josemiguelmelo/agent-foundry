"""YAML frontmatter parsing for markdown (skills, agents, CLI rewrites)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def parse_frontmatter(text: str) -> tuple[dict[str, Any] | None, str]:
    """
    Split leading YAML frontmatter from markdown.

    Returns ``(None, full_text)`` if there is no valid ``---`` block or YAML errors.
    Otherwise ``(frontmatter_dict, body)``.
    """
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---\n", 3)
    if end == -1:
        return None, text
    block = text[3:end]
    body = text[end + 5 :]
    try:
        fm = yaml.safe_load(block) or {}
    except yaml.YAMLError:
        return None, text
    if not isinstance(fm, dict):
        return None, text
    narrow = {str(k): v for k, v in fm.items()}
    return narrow, body


def split_frontmatter_for_rewrite(raw: str) -> tuple[dict[str, Any], str]:
    """
    Like :func:`parse_frontmatter` but matches legacy consumer behavior: on missing
    or invalid frontmatter, return ``({}, raw)``.
    """
    fm, body = parse_frontmatter(raw)
    if fm is None:
        return {}, raw
    return fm, body


def assemble_frontmatter_markdown(fm: dict[str, Any], body: str) -> str:
    dumped = yaml.safe_dump(
        fm,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    ).rstrip()
    sep_body = body if body.startswith("\n") else "\n" + body
    return f"---\n{dumped}\n---{sep_body}"


def parse_frontmatter_file(path: Path) -> dict[str, Any] | None:
    """Load file and return frontmatter dict, or ``None`` if absent/invalid."""
    fm, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
    return fm
