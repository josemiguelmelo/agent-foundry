"""Provider implementations keyed by CLI name."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from agent_foundry.installers.claude_provider import install_claude, uninstall_claude
from agent_foundry.installers.codex_provider import install_codex, uninstall_codex
from agent_foundry.installers.copilot_provider import install_copilot, uninstall_copilot
from agent_foundry.installers.cursor_provider import install_cursor, uninstall_cursor
from agent_foundry.installers.cursor_cli_provider import (
    install_cursor_cli,
    uninstall_cursor_cli,
)
from agent_foundry.installers.types import (
    AgentReferenceMode,
    InProjectBehavior,
    ProviderCapabilities,
    ProviderContext,
    validate_scope_behavior,
)

PROVIDER_ALIASES: dict[str, str] = {
    "cursor_cli": "cursor-cli",
}


@dataclass(frozen=True)
class Provider:
    name: str
    install_fn: Callable[..., None]
    uninstall_fn: Callable[..., None]
    capabilities: ProviderCapabilities
    scaffold_manifest_path: str | None = None
    scaffold_agents_mode: AgentReferenceMode = AgentReferenceMode.DIRECTORY

    def validate_scope(self, *, in_project: bool) -> None:
        validate_scope_behavior(self.name, self.capabilities, in_project=in_project)

    def install(self, ctx: ProviderContext) -> None:
        if ctx.plugin_root is None:
            raise RuntimeError(
                f"Provider {self.name!r}: install requires plugin_root in context."
            )
        if self.name in ("cursor-cli", "cursor"):
            self.install_fn(
                ctx.plugin_id,
                ctx.plugin_root,
                in_project=ctx.in_project,
                force=ctx.force,
            )
        else:
            self.install_fn(ctx.plugin_id, ctx.plugin_root, in_project=ctx.in_project)

    def uninstall(self, ctx: ProviderContext) -> None:
        self.uninstall_fn(ctx.plugin_id, in_project=ctx.in_project)


PROVIDERS: dict[str, Provider] = {
    "claude": Provider(
        "claude",
        install_claude,
        uninstall_claude,
        capabilities=ProviderCapabilities(in_project=InProjectBehavior.SUPPORTED),
        scaffold_manifest_path=".claude-plugin/plugin.json",
        scaffold_agents_mode=AgentReferenceMode.SINGLE_FILE,
    ),
    "codex": Provider(
        "codex",
        install_codex,
        uninstall_codex,
        capabilities=ProviderCapabilities(in_project=InProjectBehavior.SUPPORTED),
        scaffold_manifest_path=".codex-plugin/plugin.json",
        scaffold_agents_mode=AgentReferenceMode.DIRECTORY,
    ),
    "copilot": Provider(
        "copilot",
        install_copilot,
        uninstall_copilot,
        capabilities=ProviderCapabilities(
            in_project=InProjectBehavior.SUPPORTED, required_commands=("copilot",)
        ),
        scaffold_manifest_path="plugin.json",
        scaffold_agents_mode=AgentReferenceMode.SINGLE_FILE,
    ),
    "cursor": Provider(
        "cursor",
        install_cursor,
        uninstall_cursor,
        capabilities=ProviderCapabilities(in_project=InProjectBehavior.SUPPORTED),
        scaffold_manifest_path=".cursor-plugin/plugin.json",
        scaffold_agents_mode=AgentReferenceMode.DIRECTORY,
    ),
    "cursor-cli": Provider(
        "cursor-cli",
        install_cursor_cli,
        uninstall_cursor_cli,
        capabilities=ProviderCapabilities(in_project=InProjectBehavior.SUPPORTED),
        scaffold_manifest_path=None,
    ),
}


def provider_names() -> list[str]:
    return sorted(PROVIDERS)


def resolve_provider_name(raw_name: str) -> str:
    normalized = raw_name.lower()
    return PROVIDER_ALIASES.get(normalized, normalized)


def resolve_provider(raw_name: str) -> Provider:
    name = resolve_provider_name(raw_name)
    if name not in PROVIDERS:
        supported = ", ".join(provider_names())
        raise ValueError(f"Unknown provider {raw_name!r}. Supported: {supported}.")
    return PROVIDERS[name]


def scaffold_providers() -> tuple[Provider, ...]:
    return tuple(p for p in PROVIDERS.values() if p.scaffold_manifest_path)


__all__ = [
    "PROVIDERS",
    "Provider",
    "provider_names",
    "resolve_provider",
    "resolve_provider_name",
    "scaffold_providers",
]
