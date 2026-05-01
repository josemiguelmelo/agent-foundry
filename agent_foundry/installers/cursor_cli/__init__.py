"""Cursor CLI installer package."""

from .install import install_cursor_cli, uninstall_cursor_cli
from .manifest import CURSOR_MANIFEST_SUBPATH, load_cursor_plugin_manifest
from .rewrite import (
    FRONTMATTER_PLUGIN_KEY,
    iter_agent_sources,
    iter_skill_package_dirs,
    rewrite_agent_for_cli,
)
from .state import (
    CURSOR_CLI_STATE_DIRNAME,
    SCHEMA_VERSION,
    SENTINEL_NAME,
    cursor_cli_state_dir,
    load_state,
    state_path_for,
    write_skill_sentinel,
)

__all__ = [
    "CURSOR_CLI_STATE_DIRNAME",
    "CURSOR_MANIFEST_SUBPATH",
    "FRONTMATTER_PLUGIN_KEY",
    "SCHEMA_VERSION",
    "SENTINEL_NAME",
    "cursor_cli_state_dir",
    "iter_agent_sources",
    "iter_skill_package_dirs",
    "install_cursor_cli",
    "load_cursor_plugin_manifest",
    "load_state",
    "rewrite_agent_for_cli",
    "state_path_for",
    "uninstall_cursor_cli",
    "write_skill_sentinel",
]
