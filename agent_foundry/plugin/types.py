"""Typed values for plugin registry, scaffolding, and validation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict

from agent_foundry.plugin.constants import DEFAULT_AGENT_FILE
from agent_foundry.registry import parse_plugin_row

_PLUGIN_ID_RE = re.compile(r"^[a-z][a-z0-9]+(?:-[a-z0-9]+)*$")


class RegistryRow(TypedDict, total=False):
    id: str
    path: str
    version: str
    summary: str


@dataclass(frozen=True)
class Plugin:
    """One row from ``registry/plugins.yaml`` (logical plugin identity)."""

    id: str
    path: str
    version: str
    summary: str

    @classmethod
    def from_registry_row(
        cls, row: RegistryRow | dict[str, Any] | Any
    ) -> Plugin | None:
        parsed = parse_plugin_row(row)
        if not parsed:
            return None
        return cls(
            id=parsed.id,
            path=parsed.path,
            version=parsed.version,
            summary=parsed.summary,
        )

    @staticmethod
    def validate_id(plugin_id: str) -> None:
        if not plugin_id or len(plugin_id) < 2 or len(plugin_id) > 64:
            raise ValueError("Plugin id must be 2–64 characters.")
        if not _PLUGIN_ID_RE.fullmatch(plugin_id):
            raise ValueError(
                "Plugin id must be lowercase kebab-case "
                "(e.g. `my-plugin`, letters/digits/hyphens, start with a letter)."
            )


@dataclass(frozen=True)
class PluginSpec:
    """Normalized plugin inputs used by services."""

    id: str
    version: str
    summary: str
    repo_root: Path

    @property
    def plugin_dir(self) -> Path:
        return self.repo_root / "plugins" / self.id

    @property
    def agent_file_name(self) -> str:
        return DEFAULT_AGENT_FILE

    @property
    def default_agent_rel(self) -> str:
        return f"./agents/{self.agent_file_name}"

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.id,
            "version": self.version,
            "description": self.summary,
            "author": {"name": "agent-foundry"},
            "license": "Apache-2.0",
            "keywords": [self.id, "agent-foundry"],
            "skills": "./skills/",
            "mcpServers": "./.mcp.json",
        }


@dataclass(frozen=True)
class ValidationIssue:
    message: str
