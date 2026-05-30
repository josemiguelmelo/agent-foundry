# Source Path Overrides

Use repeatable `--path <kind>:<dir>` on `install-plugin` and `install` to override where skills, agents, commands, or MCP configs are read **inside the plugin** (manifest source roots).

Paths are relative to the plugin root unless absolute.

## Supported kinds

| Kind | Maps to |
| --- | --- |
| `skills` | Skill directories |
| `agents` | Agent definition files |
| `commands` | Command definitions |
| `mcp` | MCP server configs (`mcpServers` in manifests) |

Uninstall does not require `--path` — install state tracks the actual destinations.

## Examples

Registry plugin with a non-default layout:

```bash
agent-foundry install-plugin cursor-cli my-plugin \
  --path skills:./vendor/skills \
  --path agents:./vendor/agents
```

External repo with skills in a custom directory:

```bash
agent-foundry install skill cursor-cli commit \
  --repo /path/to/my-agents \
  --path skills:./alt-skills
```

## When to use

- Plugins that vendor third-party skills or agents in non-standard folders
- External repositories that do not follow the default `skills/` and `agents/` layout at the plugin root
- Migrating existing plugin trees without restructuring directories

<div class="af-related" markdown="1">

## Related

- [Installation](installation.md)
- [External repositories](external-repos.md)
- [CLI reference](cli-reference.md)

</div>
