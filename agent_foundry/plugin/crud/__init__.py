"""CRUD services for plugin management."""

from agent_foundry.plugin.crud.create_service import CreatePluginService
from agent_foundry.plugin.crud.remove_service import RemovePluginService

__all__ = ["CreatePluginService", "RemovePluginService"]
