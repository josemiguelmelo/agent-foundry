---
applyTo: "plugins/**,registry/**"
---

# Registry plugins

See [AGENTS.md](../../AGENTS.md) for full plugin layout and boundaries.

- Plugin ids: lowercase kebab-case
- `registry/plugins.yaml` must match `.agentic/plugin.yaml` name and version
- Skills: `skills/<name>/SKILL.md`; agents: `agents/<name>.md`
- After edits: `agent-foundry validate-plugins`
- Scaffold new plugins: `agent-foundry create-plugin <plugin_id>`
- Example bundle: `plugins/git/`
