"""CLI-facing plugin scaffolding and registry management."""

from agent_foundry.plugin.crud import CreatePluginService, RemovePluginService
from agent_foundry.plugin.operation import (
    CreatePluginResult,
    RemovePluginResult,
    ValidatePluginsResult,
)
from agent_foundry.plugin.types import Plugin
from agent_foundry.plugin.validation import ValidatePluginsService

__all__ = [
    "CreatePluginService",
    "CreatePluginResult",
    "Plugin",
    "RemovePluginResult",
    "RemovePluginService",
    "ValidatePluginsResult",
    "ValidatePluginsService",
]
