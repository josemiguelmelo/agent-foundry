# Installation

This page covers how to install the **agent-foundry** CLI and how plugin installation resolves its source repository.

## Install via pipx

The recommended install path uses [pipx](https://pipx.pypa.io/) so the CLI is isolated from your system Python:

```bash
pipx install git+https://github.com/josemiguelmelo/agent-foundry.git
```

For local development from a checkout:

```bash
pip install -e .
agent-foundry --help
```

## Install a plugin

Install or remove a registry plugin for a provider:

```bash
agent-foundry install-plugin <provider> <plugin_id>
agent-foundry uninstall-plugin <provider> <plugin_id>
```

Install or remove a single item (agent, skill, or MCP config):

```bash
agent-foundry install <kind> <provider> <identifier>
agent-foundry uninstall <kind> <provider> <identifier>
```

Replace:

- `<provider>` — one of: `claude`, `codex`, `copilot`, `cursor`, `cursor-cli`
- `<plugin_id>` — a plugin id from the [plugin catalog](../plugins/index.md)
- `<kind>` — one of: `agent`, `skill`, `mcp-config`
- `<identifier>` — item name (agent stem, skill folder name, or MCP server id). Use `<plugin_id>:<identifier>` when names overlap across plugins.

## Default repository resolution

By default, `install-plugin` tries to fetch the agent-foundry repository from GitHub and resolves plugin paths from that clone. If the fetch fails, it falls back to local registry discovery (useful when developing from a checkout).

## Install from a custom repository

Pass `--repo` with a **local path** or **git remote URL** (HTTPS/SSH) to install from a custom repository instead of the default fetch:

```bash
agent-foundry install-plugin cursor-cli git --repo /path/to/agent-foundry
agent-foundry install skill cursor-cli commit --repo https://github.com/org/my-agents.git
```

For a full agent-foundry checkout (with `registry/plugins.yaml`), `--repo` uses registry-based plugin lookup. Private repositories use your existing git credentials; ref/tag pinning is not supported yet.

See [External repositories](external-repos.md) for layout requirements and examples.

## Scope

By default, installs are **global** (paths under your home directory). Use `--in-project` to install into the current working directory instead.

Use the same scope for install and uninstall operations. See [Scope](scope.md) for provider-specific behavior.

<div class="af-related" markdown="1">

## Related

- [Getting started](getting-started.md)
- [CLI reference](cli-reference.md)
- [Source path overrides](source-paths.md)

</div>
