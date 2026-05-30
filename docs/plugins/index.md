# Plugin Catalog

The central registry at `registry/plugins.yaml` indexes all distributable plugins. Each plugin is a self-contained bundle of skills, agents, commands, and optional MCP configs.

## Available plugins

| Plugin | Version | Summary |
| --- | --- | --- |
| [git](git.md) | 0.1.0 | Git workflow plugin with skills for commit quality, branch creation, and PR opening |
| [software-development-agents](software-development-agents.md) | 1.0.0 | Multi-role software development team agents with per-project memory |
| [project-management](project-management.md) | 1.0.0 | Project management skills for structured issues and tasks with markdown templates |

## Install a plugin

```bash
agent-foundry install-plugin <provider> <plugin_id>
```

Example:

```bash
agent-foundry install-plugin cursor-cli git
```

Install a single skill or agent from a plugin:

```bash
agent-foundry install skill cursor-cli git:commit
agent-foundry install agent cursor software-development-agents:senior-ai-engineer
```

See [Installation](../user/installation.md) and [CLI reference](../user/cli-reference.md) for all options.

## Create your own plugin

Contributors can scaffold new plugins with `agent-foundry create-plugin`. See [Plugin development](../contributors/plugin-development.md).

<div class="af-related" markdown="1">

## Related

- [Getting started](../user/getting-started.md)
- [CLI reference](../user/cli-reference.md)
- [Plugin development](../contributors/plugin-development.md)

</div>
