"""Shared provider command logic for install/uninstall handlers."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

from agent_foundry.core.errors import AgentFoundryError, UsageError
from agent_foundry.installers import provider_names, resolve_provider
from agent_foundry.installers.specific import (
    materialized_specific_plugin,
    resolve_specific_selection,
)
from agent_foundry.installers.types import InProjectBehavior, ProviderContext
from agent_foundry.plugin.types import Plugin
from agent_foundry.registry import resolve_plugin_dir
from agent_foundry.registry.external import (
    LAYOUT_ENV,
    LAYOUT_EXTERNAL,
    LAYOUT_REGISTRY,
    is_external_repo,
    is_git_remote_url,
    is_registry_repo,
    prepared_external_plugin_root,
    shallow_clone_repo,
)

from agent_foundry.cli.exit_codes import RUNTIME_FAILURE, SUCCESS, USAGE_OR_VALIDATION

DEFAULT_REPOSITORY_URL = "https://github.com/josemiguelmelo/agent-foundry.git"


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


@contextmanager
def _with_env_var(name: str, value: str | None):
    old = os.environ.get(name)
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value
    try:
        yield
    finally:
        if old is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = old


@contextmanager
def _with_agent_foundry_repo(repo_root: Path, *, layout: str | None = None):
    with _with_env_var("AGENT_FOUNDRY_REPO", str(repo_root)):
        with _with_env_var(LAYOUT_ENV, layout):
            yield


@contextmanager
def _install_repo_context(args: argparse.Namespace):
    """Resolve repo source for install: local override, remote git clone, or default."""
    repo_arg = getattr(args, "repo", None)
    if repo_arg:
        raw = str(repo_arg).strip()
        if is_git_remote_url(raw):
            git_bin = shutil.which("git")
            if not git_bin:
                raise RuntimeError(
                    "git is required to clone --repo URL but was not found on PATH."
                )
            with tempfile.TemporaryDirectory(prefix="agent-foundry-repo-") as tmpdir:
                clone_root = Path(tmpdir) / "repo"
                shallow_clone_repo(raw, dest=clone_root)
                if is_registry_repo(clone_root):
                    layout = LAYOUT_REGISTRY
                elif is_external_repo(clone_root):
                    layout = LAYOUT_EXTERNAL
                else:
                    raise FileNotFoundError(
                        f"Cloned repository has no registry/plugins.yaml and no "
                        f"convention layout (agents/, skills/, plugins/): {clone_root}"
                    )
                with _with_agent_foundry_repo(clone_root, layout=layout):
                    yield
            return

        repo_root = Path(raw).expanduser().resolve()
        if not repo_root.is_dir():
            raise FileNotFoundError(f"--repo path is not a directory: {repo_root}")
        if is_registry_repo(repo_root):
            with _with_agent_foundry_repo(repo_root, layout=LAYOUT_REGISTRY):
                yield
            return
        if is_external_repo(repo_root):
            with _with_agent_foundry_repo(repo_root, layout=LAYOUT_EXTERNAL):
                yield
            return
        raise FileNotFoundError(
            f"--repo does not contain registry/plugins.yaml and has no convention layout "
            f"(expected agents/, skills/, or plugins/ under): {repo_root}"
        )

    git_bin = shutil.which("git")
    if git_bin:
        with tempfile.TemporaryDirectory(prefix="agent-foundry-repo-") as tmpdir:
            clone_root = Path(tmpdir) / "repo"
            result = subprocess.run(
                [git_bin, "clone", "--depth", "1", DEFAULT_REPOSITORY_URL, str(clone_root)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                with _with_agent_foundry_repo(clone_root, layout=LAYOUT_REGISTRY):
                    yield
                return
            print(
                "Warning: could not fetch repository from git; falling back to local lookup.",
                file=sys.stderr,
            )
            stderr = (result.stderr or "").strip()
            if stderr:
                print(stderr, file=sys.stderr)

    yield


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

    force = bool(getattr(args, "force", False))

    try:
        if uninstall and not getattr(args, "repo", None):
            ctx = ProviderContext(
                plugin_id=args.plugin,
                plugin_root=None,
                in_project=in_project,
                force=force,
            )
            ops.uninstall(ctx)
        else:
            with _install_repo_context(args):
                if uninstall:
                    ctx = ProviderContext(
                        plugin_id=args.plugin,
                        plugin_root=None,
                        in_project=in_project,
                        force=force,
                    )
                    ops.uninstall(ctx)
                else:
                    resolved = _ensure_resolved_plugin(args.plugin)
                    if isinstance(resolved, int):
                        return resolved
                    with prepared_external_plugin_root(resolved) as plugin_root:
                        ctx = ProviderContext(
                            plugin_id=args.plugin,
                            plugin_root=plugin_root,
                            in_project=in_project,
                            force=force,
                        )
                        ops.install(ctx)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        return USAGE_OR_VALIDATION
    except (RuntimeError, AgentFoundryError) as e:
        print(e, file=sys.stderr)
        return RUNTIME_FAILURE
    return SUCCESS


def run_provider_specific_operation(
    args: argparse.Namespace,
    *,
    uninstall: bool,
) -> int:
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

    force = bool(getattr(args, "force", False))

    try:
        with _install_repo_context(args):
            selection = resolve_specific_selection(args.kind, args.identifier)
            synthetic_plugin_id = selection.synthetic_plugin_id
            if uninstall:
                ctx = ProviderContext(
                    plugin_id=synthetic_plugin_id,
                    plugin_root=None,
                    in_project=in_project,
                    force=force,
                )
                ops.uninstall(ctx)
            else:
                with materialized_specific_plugin(selection) as plugin_root:
                    ctx = ProviderContext(
                        plugin_id=synthetic_plugin_id,
                        plugin_root=plugin_root,
                        in_project=in_project,
                        force=force,
                    )
                    ops.install(ctx)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        return USAGE_OR_VALIDATION
    except ValueError as e:
        print(e, file=sys.stderr)
        return USAGE_OR_VALIDATION
    except (RuntimeError, AgentFoundryError) as e:
        print(e, file=sys.stderr)
        return RUNTIME_FAILURE
    return SUCCESS
