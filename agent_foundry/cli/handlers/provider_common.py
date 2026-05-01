"""Shared provider command logic for install/uninstall handlers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agent_foundry.core.errors import AgentFoundryError, UsageError
from agent_foundry.installers import provider_names, resolve_provider
from agent_foundry.installers.types import InProjectBehavior, ProviderContext
from agent_foundry.plugin.types import Plugin
from agent_foundry.registry import resolve_plugin_dir

from agent_foundry.cli.exit_codes import RUNTIME_FAILURE, SUCCESS, USAGE_OR_VALIDATION


def providers_help_sentence() -> str:
    names = provider_names()
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + f", or {names[-1]}"


def add_install_scope_arguments(p: argparse.ArgumentParser) -> None:
    g = p.add_mutually_exclusive_group()
    g.add_argument(
        "--global",
        dest="scope",
        action="store_const",
        const="global",
        help="Use user-wide paths under the home directory (default).",
    )
    g.add_argument(
        "--in-project",
        dest="scope",
        action="store_const",
        const="in_project",
        help="Install or remove artifacts under the current working directory.",
    )


def _ensure_resolved_plugin(plugin: str) -> int | Path:
    """Return plugin root path or exit code."""
    try:
        return resolve_plugin_dir(plugin)
    except KeyError as e:
        print(e.args[0] if e.args else str(e), file=sys.stderr)
        return USAGE_OR_VALIDATION
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        return USAGE_OR_VALIDATION


def _validate_plugin_id(plugin: str) -> int | None:
    try:
        Plugin.validate_id(plugin)
    except ValueError as e:
        print(e, file=sys.stderr)
        return USAGE_OR_VALIDATION
    return None


def run_provider_operation(
    args: argparse.Namespace,
    *,
    uninstall: bool,
) -> int:
    invalid_plugin = _validate_plugin_id(args.plugin)
    if invalid_plugin is not None:
        return invalid_plugin

    try:
        ops = resolve_provider(args.provider)
    except ValueError as e:
        print(e, file=sys.stderr)
        return USAGE_OR_VALIDATION

    in_project = getattr(args, "scope", "global") == "in_project"
    try:
        ops.validate_scope(in_project=in_project)
    except UsageError as e:
        print(e, file=sys.stderr)
        return USAGE_OR_VALIDATION
    if in_project and ops.capabilities.in_project == InProjectBehavior.IGNORED:
        print(
            f"Note: provider {ops.name!r} ignores --in-project and always uses user scope.",
            file=sys.stderr,
        )

    root: Path | None = None
    if not uninstall:
        resolved = _ensure_resolved_plugin(args.plugin)
        if isinstance(resolved, int):
            return resolved
        root = resolved

    ctx = ProviderContext(
        plugin_id=args.plugin, plugin_root=root, in_project=in_project
    )

    try:
        if uninstall:
            ops.uninstall(ctx)
        else:
            ops.install(ctx)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        return USAGE_OR_VALIDATION
    except (RuntimeError, AgentFoundryError) as e:
        print(e, file=sys.stderr)
        return RUNTIME_FAILURE
    return SUCCESS
