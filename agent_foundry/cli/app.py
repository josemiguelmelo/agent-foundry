"""argparse wiring and CLI entrypoint."""

from __future__ import annotations

import argparse

from agent_foundry.cli.handlers import (
    add_install_scope_arguments,
    add_path_arguments,
    handle_create_plugin,
    handle_install,
    handle_install_specific,
    handle_remove_plugin,
    handle_uninstall,
    handle_uninstall_specific,
    handle_validate_plugins,
    providers_help_sentence,
)


REPO_HELP = (
    "Local repository root or git remote URL (HTTPS/SSH). "
    "Registry checkouts use registry/plugins.yaml; external repos use "
    "agents/, skills/, and plugins/ at the root. "
    "If omitted, install fetches the default agent-foundry repository first."
)


def build_parser() -> argparse.ArgumentParser:
    provider_help = f"Target tool: {providers_help_sentence()}."
    plugin_help = (
        "Plugin id from registry/plugins.yaml, or directory name under plugins/ "
        "for external repositories (e.g. my-plugin)."
    )

    parser = argparse.ArgumentParser(
        prog="agent-foundry",
        description="Install, validate, scaffold, or manage agent-foundry registry plugins.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_install = sub.add_parser(
        "install-plugin",
        help="Install a registry plugin for a provider.",
    )
    p_install.add_argument("provider", help=provider_help)
    p_install.add_argument("plugin", help=plugin_help)
    p_install.add_argument("--repo", help=REPO_HELP)
    add_install_scope_arguments(p_install)
    add_path_arguments(p_install)
    p_install.add_argument(
        "--force",
        action="store_true",
        help=(
            "Cursor CLI only: overwrite existing agent files in ~/.cursor/agents that "
            "belong to another install or were not created by agent-foundry."
        ),
    )
    p_install.set_defaults(handler=handle_install, scope="global")

    p_uninstall = sub.add_parser(
        "uninstall-plugin",
        help="Remove a registry plugin installation for a provider.",
    )
    p_uninstall.add_argument("provider", help=provider_help)
    p_uninstall.add_argument("plugin", help=plugin_help)
    p_uninstall.add_argument("--repo", help=REPO_HELP)
    add_install_scope_arguments(p_uninstall)
    p_uninstall.set_defaults(handler=handle_uninstall, scope="global")

    p_install_specific = sub.add_parser(
        "install",
        help="Install one specific kind item for a provider.",
    )
    p_install_specific.add_argument(
        "kind",
        help="Item kind (agent, skill, or mcp-config).",
    )
    p_install_specific.add_argument("provider", help=provider_help)
    p_install_specific.add_argument(
        "identifier",
        help=(
            "Unique item identifier, optionally scoped as "
            "'<plugin_id>:<identifier>' when names overlap."
        ),
    )
    p_install_specific.add_argument("--repo", help=REPO_HELP)
    add_install_scope_arguments(p_install_specific)
    add_path_arguments(p_install_specific)
    p_install_specific.add_argument(
        "--force",
        action="store_true",
        help=(
            "Cursor CLI only: overwrite existing agent files in ~/.cursor/agents that "
            "belong to another install or were not created by agent-foundry."
        ),
    )
    p_install_specific.set_defaults(handler=handle_install_specific, scope="global")

    p_uninstall_specific = sub.add_parser(
        "uninstall",
        help="Remove one specific kind item for a provider.",
    )
    p_uninstall_specific.add_argument(
        "kind",
        help="Item kind (agent, skill, or mcp-config).",
    )
    p_uninstall_specific.add_argument("provider", help=provider_help)
    p_uninstall_specific.add_argument(
        "identifier",
        help=(
            "Unique item identifier, optionally scoped as "
            "'<plugin_id>:<identifier>' when names overlap."
        ),
    )
    p_uninstall_specific.add_argument("--repo", help=REPO_HELP)
    add_install_scope_arguments(p_uninstall_specific)
    p_uninstall_specific.add_argument(
        "--force",
        action="store_true",
        help=(
            "Cursor CLI only: overwrite existing agent files in ~/.cursor/agents that "
            "belong to another install or were not created by agent-foundry."
        ),
    )
    p_uninstall_specific.set_defaults(
        handler=handle_uninstall_specific, scope="global"
    )

    p_validate = sub.add_parser(
        "validate-plugins",
        help="Validate registry/plugins.yaml and all plugin manifests.",
    )
    p_validate.set_defaults(handler=handle_validate_plugins)

    p_create = sub.add_parser(
        "create-plugin",
        help="Create a new plugin directory and append it to the registry.",
    )
    p_create.add_argument(
        "name",
        metavar="PLUGIN_ID",
        help="Plugin id (lowercase kebab-case, e.g. my-plugin).",
    )
    p_create.add_argument(
        "--version",
        default="0.1.0",
        help="Initial semver for manifests and registry (default: 0.1.0).",
    )
    p_create.add_argument(
        "--summary",
        default=None,
        help="Short description stored in manifests and registry (default: placeholder).",
    )
    p_create.set_defaults(handler=handle_create_plugin)

    p_remove = sub.add_parser(
        "remove-plugin",
        help=(
            "Drop a plugin from registry/plugins.yaml and delete plugins/<PLUGIN_ID>/."
        ),
    )
    p_remove.add_argument(
        "name",
        metavar="PLUGIN_ID",
        help="Registered plugin id to remove.",
    )
    p_remove.set_defaults(handler=handle_remove_plugin)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    code = args.handler(args)
    raise SystemExit(code)
