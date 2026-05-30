# Scope

Install scope controls whether plugin content is written to user-level paths (global) or the current project directory.

!!! warning "Use matching scope"
    Always uninstall with the same scope you used to install. Mixing `--global` and `--in-project` leaves orphaned files.

## Global vs project-local

| Scope | Flag | Root |
| --- | --- | --- |
| Global (default) | `--global` | Your home directory |
| Project-local | `--in-project` | Current working directory |

## Examples

```bash
# Global install (default)
agent-foundry install-plugin codex git

# Project-local install
agent-foundry install-plugin codex git --in-project

# Remove from project-local scope
agent-foundry uninstall-plugin codex git --in-project

# Install one skill directly into the project
agent-foundry install skill cursor-cli git:commit --in-project

# Remove one agent (global)
agent-foundry uninstall agent cursor senior-ai-engineer
```

## Provider behavior with `--in-project`

| Provider | `--in-project` behavior |
| --- | --- |
| `cursor` | Same as `cursor-cli`: `./.cursor/skills/`, `./.cursor/agents/`, state under `./.agent-foundry/cursor-cli/`. The IDE does not load `./.cursor/plugins/local/` in projects. |
| `cursor-cli` | `./.cursor/` plus state under `./.agent-foundry/cursor-cli/` |
| `codex` | `./.codex/plugins/` and `./.agents/plugins/marketplace.json` |
| `copilot` | Mirrors plugin kinds into `./.github/skills/`, `./.github/agents/`, and `./.claude/commands/` |
| `claude` | No effect — installs stay under `~/.agent-foundry/...` |

## When to use each scope

**Global (`--global`):**

- Personal workflows you want available in every project
- Cursor CLI skills and agents in `~/.cursor/`
- Default for most single-developer setups

**Project-local (`--in-project`):**

- Team-shared agent configs committed alongside the codebase
- Codex or Copilot project-specific plugin layouts
- Reproducible setups per repository

<div class="af-related" markdown="1">

## Related

- [Providers](providers.md)
- [Installation](installation.md)
- [CLI reference](cli-reference.md)

</div>
