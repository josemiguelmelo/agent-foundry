# software-development-agents

Specialized **agents** for a software team (AI, frontend, backend, architecture, product management) with **per-project memory** under `.agent-foundry/memory/software-development-agents/<agent-name>/` in each workspace.

For **parallel feature work**, the architect and team loop standardize **git worktrees** (one branch and checkout path per track).

| Field | Value |
| --- | --- |
| **Plugin id** | `software-development-agents` |
| **Version** | 1.0.0 |
| **Path** | `plugins/software-development-agents` |

!!! example "Quick install"
    ```bash
    agent-foundry install-plugin cursor-cli software-development-agents
    ```

## Install

```bash
agent-foundry install-plugin <provider> software-development-agents
```

Install a single agent:

```bash
agent-foundry install agent cursor software-development-agents:senior-ai-engineer
```

## Agents

| Agent | Role |
| --- | --- |
| `senior-ai-engineer` | AI/ML engineering workflows |
| `senior-backend-engineer` | Backend development |
| `senior-frontend-engineer` | Frontend development |
| `senior-kotlin-engineer` | Kotlin-specific development |
| `senior-product-manager` | Product management and requirements |
| `senior-pull-request-reviewer` | Code review and PR feedback |
| `senior-software-architect` | Architecture decisions and ADRs |

## Skills and commands

| Resource | Description |
| --- | --- |
| `pr-review` (skill) | Structured pull request review workflow |
| `implement-tasks` (command) | Task implementation command for supported providers |

## Per-project memory

Agents store project context under:

```
.agent-foundry/memory/software-development-agents/<agent-name>/
```

Use `--in-project` when installing to enable workspace-specific memory. See [Scope](../user/scope.md).

## Provider manifests

| Provider | Manifest |
| --- | --- |
| Cursor | `.cursor-plugin/plugin.json` |
| Claude Code | `.claude-plugin/plugin.json` |
| OpenAI Codex | `.codex-plugin/plugin.json` |
| GitHub Copilot CLI | `plugin.json` |
| Registry / CI | `.agentic/plugin.yaml` |

## Validation

```bash
agent-foundry validate-plugins
```

<div class="af-related" markdown="1">

## Related

- [Plugin catalog](index.md)
- [Installation](../user/installation.md)

</div>
