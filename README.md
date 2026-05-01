# agent-foundry

`agent-foundry` is a CLI for installing registry-defined plugins into Codex, Claude Code, Cursor (IDE and CLI), and Copilot CLI.

Plugins live under [`plugins/`](plugins/) and are indexed in [`registry/plugins.yaml`](registry/plugins.yaml).

# Quickstart

## Prerequisites

- Python 3.10+
- [pipx](https://pipx.pypa.io/)

## Installation via CLI

1. Install the CLI:

   ```bash
   pipx install git+https://github.com/josemiguelmelo/agent-foundry.git
   ```

2. Install or remove a plugin for a provider:

   ```bash
   agent-foundry install <provider> <plugin_id>
   agent-foundry uninstall <provider> <plugin_id>
   ```

   Replace:
  - `<provider>` with one of: `claude`, `codex`, `copilot`, `cursor`, `cursor-cli`
   - `<plugin_id>` with a plugin id from [`registry/plugins.yaml`](registry/plugins.yaml)

# Usage

Use this command to see available options at any time:

```bash
agent-foundry --help
```

## Providers

- Supported providers: `claude`, `codex`, `copilot`, `cursor`, `cursor-cli`
- `cursor-cli` mirrors plugin skills and agents into Cursor CLI discovery paths (`~/.cursor/skills/` and `~/.cursor/agents/`) when using global scope

## Scope

- Default scope is `--global` (paths under your home directory)
- `--in-project` uses the current working directory as the root
- Use the same scope for `install` and `uninstall`

Examples:

```bash
# Global install (default)
agent-foundry install codex <plugin_id>

# Project-local install
agent-foundry install codex <plugin_id> --in-project

# Remove from project-local scope
agent-foundry uninstall codex <plugin_id> --in-project
```

| Provider | `--in-project` behavior |
| --- | --- |
| `cursor` | `./.cursor/plugins/local/<plugin_id>/` |
| `cursor-cli` | `./.cursor/` plus state under `./.agent-foundry/cursor-cli/` |
| `codex` | `./.codex/plugins/` and `./.agents/plugins/marketplace.json` |
| `copilot` | Not supported (user scope only) |
| `claude` | No effect — installs stay under `~/.agent-foundry/...` |

## Repository Commands

Run from the repository root with the CLI available:

```bash
agent-foundry validate-plugins
agent-foundry create-plugin <plugin_id> [--version 0.1.0] [--summary "…"]
agent-foundry remove-plugin <plugin_id>
```

- `create-plugin` requires lowercase kebab-case plugin ids
- `remove-plugin` deletes `plugins/<plugin_id>/` and its registry entry (it does not uninstall from Codex/Claude/etc.)

# Contribution

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

Licensed under Apache-2.0 — [`LICENSE`](LICENSE).
