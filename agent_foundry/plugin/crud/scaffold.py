"""Plugin scaffold templates and provider manifest strategies."""

from __future__ import annotations

import yaml

from agent_foundry.installers import scaffold_providers
from agent_foundry.installers.types import AgentReferenceMode
from agent_foundry.plugin.constants import (
    AGENTIC_MANIFEST_REL,
    AGENTS_DIR,
    MCP_MANIFEST_FILE,
    SKILLS_DIR,
)
from agent_foundry.plugin.types import PluginSpec
from agent_foundry.utils.json_io import write_json


def starter_skill_md(plugin_id: str) -> str:
    return f"""---
name: example
description: Starter skill for plugin {plugin_id}. Replace this with real workflows.
---

## When to use

- When you need the default scaffolding instructions for `{plugin_id}`.

## Instructions

Customize this skill and add more under `skills/<name>/SKILL.md`.
"""


def starter_agent_md(plugin_id: str) -> str:
    return f"""---
name: default
description: Default subagent scaffold for `{plugin_id}`. Specialized agents go in separate files here.
---

## Role

Assist with `{plugin_id}` scoped tasks until you split work into focused agents under `agents/`.

## Guidelines

- Prefer small, testable edits.
"""


def readme_md(plugin_id: str) -> str:
    return f"""# {plugin_id}

Starter multi-provider plugin (Cursor, Claude Code, OpenAI Codex, Copilot CLI, registry).

Browse `skills/` and `agents/` in this folder. Validate with:

`agent-foundry validate-plugins`
"""


def write_provider_manifests(spec: PluginSpec) -> None:
    for provider in scaffold_providers():
        if not provider.scaffold_manifest_path:
            continue
        manifest = spec.to_json()
        manifest["agents"] = (
            [spec.default_agent_rel]
            if provider.scaffold_agents_mode == AgentReferenceMode.SINGLE_FILE
            else "./agents"
        )
        target = spec.plugin_dir / provider.scaffold_manifest_path
        target.parent.mkdir(parents=True, exist_ok=True)
        write_json(target, manifest)


def write_base_scaffold(spec: PluginSpec) -> None:
    plugin_dir = spec.plugin_dir
    (plugin_dir / ".agentic").mkdir(parents=True, exist_ok=True)
    (plugin_dir / ".cursor-plugin").mkdir(parents=True, exist_ok=True)
    (plugin_dir / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (plugin_dir / ".codex-plugin").mkdir(parents=True, exist_ok=True)
    (plugin_dir / SKILLS_DIR / "example").mkdir(parents=True, exist_ok=True)
    (plugin_dir / AGENTS_DIR).mkdir(parents=True, exist_ok=True)

    plugin_yaml = {
        "name": spec.id,
        "version": spec.version,
        "description": spec.summary,
    }
    (plugin_dir / AGENTIC_MANIFEST_REL).write_text(
        yaml.safe_dump(
            plugin_yaml,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        ).rstrip()
        + "\n",
        encoding="utf-8",
    )

    write_json(plugin_dir / MCP_MANIFEST_FILE, {"mcpServers": {}})
    (plugin_dir / SKILLS_DIR / "example" / "SKILL.md").write_text(
        starter_skill_md(spec.id), encoding="utf-8"
    )
    (plugin_dir / AGENTS_DIR / spec.agent_file_name).write_text(
        starter_agent_md(spec.id), encoding="utf-8"
    )
    (plugin_dir / "README.md").write_text(readme_md(spec.id), encoding="utf-8")

    write_provider_manifests(spec)
