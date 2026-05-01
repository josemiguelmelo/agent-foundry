"""Typed provider contracts and operation context."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol

from agent_foundry.core.errors import UsageError


class InProjectBehavior(str, Enum):
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    IGNORED = "ignored"


class AgentReferenceMode(str, Enum):
    DIRECTORY = "directory"
    SINGLE_FILE = "single_file"


@dataclass(frozen=True)
class ProviderCapabilities:
    in_project: InProjectBehavior = InProjectBehavior.SUPPORTED
    required_commands: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProviderContext:
    plugin_id: str
    plugin_root: Path | None
    in_project: bool


class ProviderContract(Protocol):
    name: str
    capabilities: ProviderCapabilities

    def validate_scope(self, *, in_project: bool) -> None:
        ...

    def install(self, ctx: ProviderContext) -> None:
        ...

    def uninstall(self, ctx: ProviderContext) -> None:
        ...


def validate_scope_behavior(
    provider_name: str,
    capabilities: ProviderCapabilities,
    *,
    in_project: bool,
) -> None:
    if not in_project:
        return
    behavior = capabilities.in_project
    if behavior == InProjectBehavior.SUPPORTED:
        return
    if behavior == InProjectBehavior.IGNORED:
        return
    raise UsageError(f"--in-project is not supported for provider {provider_name!r}.")

