# project-management

Project management plugin with skills for structured issues and tasks with consistent markdown templates.

| Field | Value |
| --- | --- |
| **Plugin id** | `project-management` |
| **Version** | 1.0.0 |
| **Path** | `plugins/project-management` |

!!! example "Quick install"
    ```bash
    agent-foundry install-plugin cursor-cli project-management
    ```

## Install

```bash
agent-foundry install-plugin <provider> project-management
```

Install the create-issue skill directly:

```bash
agent-foundry install skill cursor-cli project-management:create-issue
```

## Skills

| Skill | Description |
| --- | --- |
| `create-issue` | Creates tracked issues with a fixed markdown template (metadata, summary, goals, scope, acceptance criteria) via GitHub CLI, GitLab CLI, or Jira MCP |

## Validation

```bash
agent-foundry validate-plugins
```

<div class="af-related" markdown="1">

## Related

- [Plugin catalog](index.md)
- [Installation](../user/installation.md)

</div>
