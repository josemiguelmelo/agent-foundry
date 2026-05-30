# CLI Reference

Run `agent-foundry --help` at any time for the latest option list.

!!! tip "Quick help"
    Every command below accepts `--help`. Example: `agent-foundry install-plugin --help`

## Providers

All install and uninstall commands require a `<provider>`:

| Provider | Description |
| --- | --- |
| `claude` | Claude Code |
| `codex` | OpenAI Codex |
| `copilot` | GitHub Copilot CLI |
| `cursor` | Cursor IDE |
| `cursor-cli` | Cursor CLI |

See [Providers](providers.md) and [Scope](scope.md) for install-path behavior.

## Shared flags

These flags apply to install commands (`install-plugin`, `install`):

| Flag | Description |
| --- | --- |
| `--repo PATH_OR_URL` | Local repository root or git remote URL. Registry checkouts use `registry/plugins.yaml`; external repos use `agents/`, `skills/`, and `plugins/` at the root. If omitted, install fetches the default agent-foundry repository first. |
| `--global` | Install to user-level paths (default). |
| `--in-project` | Install relative to the current working directory. |
| `--path <kind>:<dir>` | Repeatable. Override source directories inside the plugin. Kinds: `skills`, `agents`, `commands`, `mcp`. See [Source path overrides](source-paths.md). |
| `--force` | Cursor CLI only: overwrite existing agent files in `~/.cursor/agents/` that belong to another install or were not created by agent-foundry. |

Uninstall commands accept `--repo`, `--global`, and `--in-project`. Uninstall does not require `--path` (install state tracks destinations).

---

## install-plugin

Install a registry plugin for a provider.

```bash
agent-foundry install-plugin <provider> <plugin_id> [options]
```

**Arguments:**

- `provider` — target tool (see table above)
- `plugin_id` — plugin id from the registry, or directory name under `plugins/` for external repositories

**Examples:**

```bash
agent-foundry install-plugin cursor-cli git
agent-foundry install-plugin codex software-development-agents --in-project
agent-foundry install-plugin cursor-cli my-plugin --repo https://github.com/org/my-agents.git
```

---

## uninstall-plugin

Remove a registry plugin installation for a provider.

```bash
agent-foundry uninstall-plugin <provider> <plugin_id> [options]
```

Use the same `--global` / `--in-project` scope as the original install.

**Example:**

```bash
agent-foundry uninstall-plugin codex git --in-project
```

---

## install

Install one specific kind item for a provider.

```bash
agent-foundry install <kind> <provider> <identifier> [options]
```

**Arguments:**

- `kind` — `agent`, `skill`, or `mcp-config`
- `provider` — target tool
- `identifier` — unique item name; use `<plugin_id>:<identifier>` when names overlap

**Examples:**

```bash
agent-foundry install skill cursor-cli git:commit --in-project
agent-foundry install agent cursor senior-ai-engineer
agent-foundry install skill cursor-cli commit --repo https://github.com/org/my-agents.git
```

---

## uninstall

Remove one specific kind item for a provider.

```bash
agent-foundry uninstall <kind> <provider> <identifier> [options]
```

**Example:**

```bash
agent-foundry uninstall agent cursor senior-ai-engineer
```

---

## validate-plugins

Validate `registry/plugins.yaml` and all plugin manifests. Run from the repository root during development.

```bash
agent-foundry validate-plugins
```

No arguments. Exits non-zero if validation fails.

---

## create-plugin

Create a new plugin directory and append it to the registry.

```bash
agent-foundry create-plugin <plugin_id> [--version VERSION] [--summary "TEXT"]
```

**Arguments:**

- `plugin_id` — lowercase kebab-case id (e.g. `my-plugin`)

**Options:**

- `--version` — initial semver (default: `0.1.0`)
- `--summary` — short description for manifests and registry

**Example:**

```bash
agent-foundry create-plugin my-workflow --version 0.1.0 --summary "My custom workflow plugin"
```

See [Plugin development](../contributors/plugin-development.md) for layout details.

---

## remove-plugin

Drop a plugin from `registry/plugins.yaml` and delete `plugins/<plugin_id>/`.

```bash
agent-foundry remove-plugin <plugin_id>
```

This only affects the repository — it does **not** uninstall from user machines.

**Example:**

```bash
agent-foundry remove-plugin my-workflow
```

---

## Repository maintenance commands

These commands are intended for contributors working in the agent-foundry repository:

| Command | Purpose |
| --- | --- |
| `validate-plugins` | Check registry and manifest consistency |
| `create-plugin` | Scaffold a new plugin |
| `remove-plugin` | Remove a plugin from the registry |

<div class="af-related" markdown="1">

## Related

- [Installation](installation.md)
- [External repositories](external-repos.md)
- [Contributing](../contributors/contributing.md)

</div>
