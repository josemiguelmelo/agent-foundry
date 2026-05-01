"""Command handlers package."""

from .plugin import (
    handle_create_plugin,
    handle_remove_plugin,
    handle_validate_plugins,
    handle_install,
    handle_uninstall,
)
from .provider_common import (
    add_install_scope_arguments,
    providers_help_sentence,
)

__all__ = [
    "add_install_scope_arguments",
    "handle_create_plugin",
    "handle_install",
    "handle_remove_plugin",
    "handle_uninstall",
    "handle_validate_plugins",
    "providers_help_sentence",
]
