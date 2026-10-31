# devops

DevOps **agent** and **skills** for infrastructure as code, delivery pipelines, and safe releases.

| Field | Value |
| --- | --- |
| **Plugin id** | `devops` |
| **Version** | 1.0.0 |
| **Path** | `plugins/devops` |

!!! example "Quick install"
    ```bash
    agent-foundry install-plugin cursor-cli devops
    ```

## Install

```bash
agent-foundry install-plugin <provider> devops
```

Install a single resource:

```bash
agent-foundry install agent cursor devops:senior-devops-engineer
agent-foundry install skill cursor devops:iac-review
```

## Agents

| Agent | Role |
| --- | --- |
| `senior-devops-engineer` | Infrastructure as code, CI/CD pipelines, observability, and release safety |

## Skills

| Skill | Description |
| --- | --- |
| `iac-review` | Reviews Terraform/OpenTofu, Pulumi, CloudFormation, and Kubernetes changes for blast radius, security, and rollback safety |
| `ci-cd-pipeline` | Designs or updates pipelines with fast feedback, least-privilege credentials, quality gates, and immutable artifacts |

## Per-project memory

The agent stores project context under:

```
.agent-foundry/memory/devops/senior-devops-engineer/
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
