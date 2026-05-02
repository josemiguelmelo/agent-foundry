# software-development-agents

Specialized **agents** for a software team (AI, frontend, backend, architecture, product management) with **per-project memory** under `.agent-foundry/memory/software-development-agents/<agent-name>/` in each workspace.

| Provider | Manifest |
|----------|----------|
| Cursor | [`.cursor-plugin/plugin.json`](.cursor-plugin/plugin.json) |
| Claude Code | [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) |
| OpenAI Codex | [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json) |
| GitHub Copilot CLI | [`plugin.json`](plugin.json) |
| Registry / CI | [`.agentic/plugin.yaml`](.agentic/plugin.yaml) + [`registry/plugins.yaml`](../../registry/plugins.yaml) |

Install and validation patterns match other plugins in this repository; see [`plugins/development/README.md`](../development/README.md) for provider-specific commands. Validate with:

`agent-foundry validate-plugins`

## License

Apache-2.0 — see repository [`LICENSE`](../../LICENSE).
