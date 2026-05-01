# development

Shared **skills**, **agents**, and **MCP** with one manifest per tool. Lifecycle **hooks** are not part of this plugin yet (schemas differ by vendor).

| Provider | Manifest |
|----------|----------|
| Cursor | [`.cursor-plugin/plugin.json`](.cursor-plugin/plugin.json) |
| Claude Code | [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) |
| OpenAI Codex | [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json) |
| GitHub Copilot CLI | [`plugin.json`](plugin.json) |
| Registry / CI | [`.agentic/plugin.yaml`](.agentic/plugin.yaml) + [`registry/plugins.yaml`](../../registry/plugins.yaml) |

## Install hints

- **Cursor (IDE):** copy the folder (symlinks often **do not** show up locally):\
  `rm -rf ~/.cursor/plugins/local/development && cp -R /absolute/path/to/agent-foundry/plugins/development ~/.cursor/plugins/local/` then reload. Use `agent-foundry install cursor development` which copies for the same reason.
- **Cursor (`cursor-agent` / CLI parity):** The IDE loads plugin bundles under `~/.cursor/plugins/local/`; **`cursor-agent` often skips plugin-local skills.** Run **`agent-foundry install cursor-cli development`** to copy skill folders to **`~/.cursor/skills/<skill-name>/`** and agents to **`~/.cursor/agents/<plugin_id>__<basename>.md`** (namespaced). State and uninstall: **`agent-foundry uninstall cursor-cli development`** (`~/.agent-foundry/cursor-cli/<plugin_id>.json`). MCP and other manifest keys are unchanged by `cursor-cli` (skills + agents only). Compatibility alias: `cursor_cli`.
- **Claude Code (CLI install):** `agent-foundry install claude development` copies the plugin to `~/.agent-foundry/claude-marketplace/local-bundle/plugins/development`, writes a minimal marketplace manifest there, runs `claude plugin marketplace add` on that directory, then installs **`development@agent-foundry-local`**. Set `AGENT_FOUNDRY_REPO=/absolute/path/to/agent-foundry` if you run the CLI outside the clone. The repo does **not** need `.claude-plugin/marketplace.json` for this path. If install fails, check `claude plugin marketplace list` and remove a stale **agent-foundry-local** source if needed. The Claude CLI validator (`claude plugin validate plugins/development`) requires `agents` in `.claude-plugin/plugin.json` to be a **list of agent `.md` paths**, not a single directory string. Uninstall: `agent-foundry uninstall claude development` (or `claude plugin uninstall development@agent-foundry-local`). If you previously used the repo-root marketplace, remove that install with `claude plugin uninstall development@agent-foundry`.
- **Claude Code (optional repo marketplace):** If you maintain [`.claude-plugin/marketplace.json`](../../.claude-plugin/marketplace.json) at the repo root, you can still use `claude plugin marketplace add /path/to/agent-foundry` and `claude plugin install development@agent-foundry` manually.
- **Claude Code (dev):** `claude --plugin-dir /path/to/agent-foundry/plugins/development` skips the marketplace.
- **Codex:** add to `marketplace.json` per [Codex plugin docs](https://developers.openai.com/codex/plugins/build); restart after changes.
- **Copilot CLI:** `copilot plugin install ./plugins/development`; reinstall after local edits (cache).

## Version bumps

Keep `version` in sync across **`.agentic/plugin.yaml`**, **`registry/plugins.yaml`**, and all **`plugin.json`** files.

## License

Apache-2.0 — see repository [`LICENSE`](../../LICENSE).
