from __future__ import annotations

import argparse
import sys
from agent_foundry.cli.exit_codes import (
    SUCCESS,
    USAGE_OR_VALIDATION,
    RUNTIME_FAILURE,
)
from agent_foundry.cli.handlers.common import run_with_errors
from agent_foundry.cli.handlers.provider_common import run_provider_operation
from agent_foundry.plugin import ValidatePluginsService
from agent_foundry.plugin.crud import CreatePluginService, RemovePluginService


def handle_install(args: argparse.Namespace) -> int:
    return run_provider_operation(args, uninstall=False)


def handle_uninstall(args: argparse.Namespace) -> int:
    return run_provider_operation(args, uninstall=True)


def handle_create_plugin(args: argparse.Namespace) -> int:
    service = CreatePluginService()

    def _run() -> int:
        result = service.run(args.name, version=args.version, summary=args.summary)
        for msg in result.messages:
            print(msg, file=sys.stderr)
        for warning in result.warnings:
            print(warning, file=sys.stderr)
        return SUCCESS

    return run_with_errors(
        _run,
        {
            ValueError: USAGE_OR_VALIDATION,
            FileNotFoundError: USAGE_OR_VALIDATION,
            FileExistsError: RUNTIME_FAILURE,
        },
    )


def handle_remove_plugin(args: argparse.Namespace) -> int:
    service = RemovePluginService()

    def _run() -> int:
        result = service.run(args.name)
        for msg in result.messages:
            print(msg, file=sys.stderr)
        for warning in result.warnings:
            print(warning, file=sys.stderr)
        return SUCCESS

    return run_with_errors(
        _run,
        {
            ValueError: USAGE_OR_VALIDATION,
            FileNotFoundError: USAGE_OR_VALIDATION,
        },
    )


def handle_validate_plugins(_args: argparse.Namespace) -> int:
    service = ValidatePluginsService()

    def _run() -> int:
        result = service.run()
        for msg in result.messages:
            print(msg, file=sys.stderr if result.exit_code else sys.stdout)
        for issue in result.issue_messages:
            print(issue, file=sys.stderr)
        for warning in result.warnings:
            print(warning, file=sys.stderr)
        return USAGE_OR_VALIDATION if result.exit_code else SUCCESS

    return run_with_errors(
        _run,
        {
            FileNotFoundError: USAGE_OR_VALIDATION,
        },
    )
