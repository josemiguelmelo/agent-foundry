# Providers

**agent-foundry** supports five provider targets. Each maps plugin content (skills, agents, commands, MCP configs) to the discovery paths expected by that tool.

## Supported providers

| Provider | Tool | Notes |
| --- | --- | --- |
| `claude` | Claude Code | Installs under `~/.agent-foundry/...` |
| `codex` | OpenAI Codex | Project installs use `./.codex/plugins/` |
| `copilot` | GitHub Copilot CLI | Project installs mirror into `./.github/skills/`, `./.github/agents/`, and `./.claude/commands/` |
| `cursor` | Cursor IDE | Same project behavior as `cursor-cli` |
| `cursor-cli` | Cursor CLI | Mirrors skills and agents into `~/.cursor/skills/` and `~/.cursor/agents/` (global scope) |

## Cursor CLI behavior

`cursor-cli` mirrors plugin skills and agents into Cursor CLI discovery paths when using global scope:

- Skills → `~/.cursor/skills/<skill-name>/`
- Agents → `~/.cursor/agents/<agent-name>.md`
- Install state → `~/.agent-foundry/cursor-cli/`

The `--force` flag is available on Cursor CLI install commands to overwrite agent files that were not created by agent-foundry.

## Project-local behavior

When you pass `--in-project`, each provider writes to different project paths. See the full table in [Scope](scope.md).

## Install kinds

For granular installs with `install` / `uninstall`, supported kinds are:

| Kind | Description |
| --- | --- |
| `agent` | A single agent definition (`.md` file) |
| `skill` | A single skill directory with `SKILL.md` |
| `mcp-config` | An MCP server configuration entry |

Use `<plugin_id>:<identifier>` when the same name exists in multiple plugins.

## Examples

```bash
# Claude Code
agent-foundry install-plugin claude git

# Codex (project-local)
agent-foundry install-plugin codex git --in-project

# Cursor CLI (global)
agent-foundry install-plugin cursor-cli software-development-agents

# Copilot CLI
agent-foundry install-plugin copilot project-management
```

<div class="af-related" markdown="1">

## Related

- [Scope](scope.md) — global vs `--in-project` paths per provider
- [Installation](installation.md)
- [CLI reference](cli-reference.md)

</div>
