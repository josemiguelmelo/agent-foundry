# External Repositories

Use `--repo` to install plugins, agents, or skills from a git remote URL or local directory instead of the default agent-foundry fetch.

## Repository layout

External repositories do not require `registry/plugins.yaml`. They follow this layout:

```
repo-root/
  agents/
    senior-reviewer.md
  skills/
    commit/
      SKILL.md
  plugins/
    my-plugin/
      agents/
        plugin-agent.md
      skills/
        plugin-skill/
          SKILL.md
```

## Full agent-foundry checkout

When `--repo` points to a full agent-foundry checkout (with `registry/plugins.yaml`), plugin lookup uses the registry as usual. This is useful for development or installing from a fork.

Private repositories use your existing git credentials. Ref/tag pinning is not supported yet.

## Examples

Replace the URL with your repository:

```bash
# Standalone skill from repo root
agent-foundry install skill cursor-cli commit --repo https://github.com/org/my-agents.git

# Standalone agent from repo root
agent-foundry install agent cursor-cli senior-reviewer --repo https://github.com/org/my-agents.git

# Full plugin directory under plugins/
agent-foundry install-plugin cursor-cli my-plugin --repo https://github.com/org/my-agents.git

# Skill inside a plugin (scoped identifier)
agent-foundry install skill cursor-cli my-plugin:plugin-skill --repo https://github.com/org/my-agents.git

# Agent inside a plugin
agent-foundry install agent cursor-cli my-plugin:plugin-agent --repo https://github.com/org/my-agents.git
```

## Local path

`--repo` also accepts a local directory path:

```bash
agent-foundry install-plugin cursor-cli git --repo /path/to/agent-foundry
agent-foundry install skill cursor-cli commit --repo /path/to/my-agents
```

## Source path overrides

External repos with non-standard directory layouts can use `--path` to redirect where skills, agents, and other content are read. See [Source path overrides](source-paths.md).

<div class="af-related" markdown="1">

## Related

- [Installation](installation.md)
- [CLI reference](cli-reference.md)
- [Plugin development](../contributors/plugin-development.md)

</div>
