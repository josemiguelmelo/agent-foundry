"""Shared types and helpers for specific artifact selection."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_KIND_ALIASES = {
    "agent": "agent",
    "agents": "agent",
    "skill": "skill",
    "skills": "skill",
    "mcp": "mcp_config",
    "mcp-config": "mcp_config",
    "mcp_config": "mcp_config",
    "mcp-configs": "mcp_config",
}


@dataclass(frozen=True)
class SpecificSelection:
    kind: str
    source_plugin_id: str
    source_path: Path
    resolved_identifier: str

    @property
    def synthetic_plugin_id(self) -> str:
        return safe_plugin_id(
            f"specific-{self.kind}-{self.source_plugin_id}-{self.resolved_identifier}"
        )


def safe_plugin_id(value: str) -> str:
    slug = re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    if not slug:
        slug = "specific-item"
    if not slug[0].isalpha():
        slug = f"s-{slug}"
    if len(slug) == 1:
        slug = f"{slug}x"
    return slug[:64]


def normalize_kind(kind: str) -> str:
    normalized = _KIND_ALIASES.get(kind.strip().lower())
    if not normalized:
        supported = ", ".join(sorted(set(_KIND_ALIASES.values())))
        raise ValueError(f"Unknown kind {kind!r}. Supported kinds: {supported}.")
    return normalized


def split_scoped_identifier(identifier: str) -> tuple[str | None, str]:
    raw = identifier.strip()
    if not raw:
        raise ValueError("identifier cannot be empty.")
    if ":" not in raw:
        return None, raw
    plugin_id, item_id = raw.split(":", 1)
    plugin_id = plugin_id.strip()
    item_id = item_id.strip()
    if not plugin_id or not item_id:
        raise ValueError(
            "Scoped identifiers must look like '<plugin_id>:<identifier>'."
        )
    return plugin_id, item_id
