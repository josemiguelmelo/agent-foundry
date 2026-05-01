"""Operation result models for CLI-facing services."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, kw_only=True)
class OperationResult:
    messages: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, kw_only=True)
class CreatePluginResult(OperationResult):
    plugin_dir: Path


@dataclass(frozen=True, kw_only=True)
class RemovePluginResult(OperationResult):
    removed_dir: Path | None = None


@dataclass(frozen=True, kw_only=True)
class ValidatePluginsResult(OperationResult):
    exit_code: int = 0
    issue_messages: tuple[str, ...] = ()
