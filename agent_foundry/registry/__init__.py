"""Shared registry API used by plugin and installer modules."""

from agent_foundry.registry.core import (
    REGISTRY_REL,
    RegistryPlugin,
    find_registry_file,
    get_registry_plugin,
    list_registry_plugins,
    load_registry,
    parse_plugin_row,
    repository_root,
    resolve_plugin_dir,
)
from agent_foundry.registry.document import (
    REGISTRY_HEADER,
    load_document,
    plugins_list_mut,
    save_document,
)
from agent_foundry.registry.repository import RegistryRepository, RegistrySession

__all__ = [
    "REGISTRY_HEADER",
    "REGISTRY_REL",
    "RegistryPlugin",
    "find_registry_file",
    "get_registry_plugin",
    "list_registry_plugins",
    "load_document",
    "load_registry",
    "parse_plugin_row",
    "plugins_list_mut",
    "repository_root",
    "resolve_plugin_dir",
    "save_document",
    "RegistryRepository",
    "RegistrySession",
]
