# Getting Started

**agent-foundry** is a CLI for installing registry-defined plugins into Codex, Claude Code, Cursor (IDE and CLI), and Copilot CLI.

Plugins live in the repository under `plugins/` and are indexed in `registry/plugins.yaml`. You install bundles (or individual agents, skills, and MCP configs) into the AI tool you use day to day.

!!! info "What you'll need"
    Python 3.10+ and [pipx](https://pipx.pypa.io/). The whole setup takes about two minutes.

## Prerequisites

- Python 3.10+
- [pipx](https://pipx.pypa.io/) (recommended for installing the CLI)

## Install the CLI

```bash
pipx install git+https://github.com/josemiguelmelo/agent-foundry.git
```

Verify the install:

```bash
agent-foundry --help
```

## Install your first plugin

Replace `<provider>` with your target tool and `<plugin_id>` with a plugin from the [plugin catalog](../plugins/index.md):

```bash
agent-foundry install-plugin <provider> <plugin_id>
```

Example — install the **git** plugin for Cursor CLI:

```bash
agent-foundry install-plugin cursor-cli git
```

## Supported providers

| Provider | Tool |
| --- | --- |
| `claude` | Claude Code |
| `codex` | OpenAI Codex |
| `copilot` | GitHub Copilot CLI |
| `cursor` | Cursor IDE |
| `cursor-cli` | Cursor CLI |

See [Providers](providers.md) for install-path details and [Scope](scope.md) for global vs project-local installs.

<div class="af-related" markdown="1">

## Next steps

- [Installation](installation.md) — pipx, `--repo`, and external git repositories
- [CLI Reference](cli-reference.md) — all subcommands and flags
- [Plugin catalog](../plugins/index.md) — browse available plugins
- [External repositories](external-repos.md) — install from your own git repo

</div>
