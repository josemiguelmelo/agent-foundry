# devops

DevOps **agent** and **skills** for infrastructure as code and delivery pipelines.

- `senior-devops-engineer` — owns IaC, CI/CD, observability, and safe releases with per-project memory under `.agent-foundry/memory/devops/senior-devops-engineer/`.
- `iac-review` — reviews Terraform/OpenTofu, Pulumi, CloudFormation, and Kubernetes changes for blast radius, security, and rollback safety.
- `ci-cd-pipeline` — designs or updates pipelines with fast feedback, least-privilege credentials, quality gates, and immutable artifacts.

| Provider | Manifest |
|----------|----------|
| Cursor | [`.cursor-plugin/plugin.json`](.cursor-plugin/plugin.json) |
| Claude Code | [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) |
| OpenAI Codex | [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json) |
| GitHub Copilot CLI | [`plugin.json`](plugin.json) |
| Registry / CI | [`.agentic/plugin.yaml`](.agentic/plugin.yaml) + [`registry/plugins.yaml`](../../registry/plugins.yaml) |

Install:

```bash
agent-foundry install-plugin cursor-cli devops
agent-foundry install agent cursor devops:senior-devops-engineer
agent-foundry install skill cursor devops:iac-review
```

Validate with:

`agent-foundry validate-plugins`

## License

Apache-2.0 — see repository [`LICENSE`](../../LICENSE).
