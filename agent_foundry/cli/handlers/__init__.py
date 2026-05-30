"""Command handlers package."""

from .plugin import (
    handle_create_plugin,
    handle_remove_plugin,
    handle_validate_plugins,
    handle_install,
    handle_install_specific,
    handle_uninstall,
    handle_uninstall_specific,
)
from .provider_common import (
    add_install_scope_arguments,
    add_path_arguments,
    providers_help_sentence,
)

__all__ = [
    "add_install_scope_arguments",
    "add_path_arguments",
    "handle_create_plugin",
    "handle_install",
    "handle_install_specific",
    "handle_remove_plugin",
    "handle_uninstall",
    "handle_uninstall_specific",
    "handle_validate_plugins",
    "providers_help_sentence",
]
