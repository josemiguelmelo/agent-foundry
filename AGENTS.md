# Agent instructions for agent-foundry

This file is the canonical guide for AI coding agents working in this repository. Tool-specific files (`.cursor/rules/`, `.github/copilot-instructions.md`, `CLAUDE.md`) point here for full detail.

## Project purpose

**agent-foundry** is a Python CLI that installs registry-defined plugins into:

- `claude` — Claude Code
- `codex` — OpenAI Codex
- `copilot` — GitHub Copilot CLI
- `cursor` — Cursor IDE
- `cursor-cli` — Cursor CLI (mirrors skills/agents into `~/.cursor/` or `./.cursor/`)

Plugins live under `plugins/` and are indexed in `registry/plugins.yaml`. End users install bundles; this repo also contains the CLI implementation and validation logic.

## Repository map

| Path | Purpose |
| --- | --- |
| `agent_foundry/` | CLI entrypoint, registry loading, per-provider installers, plugin validation and scaffolding |
| `plugins/` | Distributable plugin bundles (skills, agents, commands, MCP configs) |
| `registry/plugins.yaml` | Central plugin index (id, path, version, summary) |
| `tests/` | Unit tests (`unittest`) |
| `scripts/e2e-cli.sh`, `e2e.md` | Optional manual end-to-end smoke tests |
| `pyproject.toml` | Package metadata and `agent-foundry` console script |

Do not treat `build/`, `*.egg-info/`, or local install state under `~/.agent-foundry/` as source of truth.

## Setup and validation commands

Run from the repository root after changes:

```bash
pip install -e .
agent-foundry --help
agent-foundry validate-plugins
python -m unittest discover -s tests -p "test_*.py"
pip install vulture
vulture agent_foundry tests --min-confidence 100
```

Optional: `scripts/e2e-cli.sh` (see `e2e.md`).

CI runs the same checks in `.github/workflows/agent-foundry-ci.yml`. The aggregate job `required-checks` must pass before merge.

## Architecture

```text
registry/plugins.yaml  →  RegistryRepository
                              ↓
plugins/<id>/          →  validate-plugins (ManifestConsistency, BundleStructure)
                              ↓
agent_foundry/installers/*_provider.py  →  install-plugin / install / uninstall
```

Key modules:

- **`agent_foundry/cli/app.py`** — argparse wiring; subcommands: `install-plugin`, `install`, `uninstall`, `validate-plugins`, `create-plugin`, `remove-plugin`
- **`agent_foundry/registry/`** — loads and parses `registry/plugins.yaml`; external repo layout in `external.py`
- **`agent_foundry/installers/`** — one module per provider (`cursor_provider.py`, `cursor_cli_provider.py`, `claude_provider.py`, `codex_provider.py`, `copilot_provider.py`); shared selection and source-path logic
- **`agent_foundry/plugin/validation/rules.py`** — duplicate plugin ids; manifest `name`/`version` must match registry; bundle structure; skill/agent frontmatter
- **`agent_foundry/plugin/crud/`** — `create-plugin` scaffold, `remove-plugin`

Cursor CLI install mirrors plugin skills to `.cursor/skills/<name>/` and agents to `.cursor/agents/`, with state under `.agent-foundry/cursor-cli/`.

## Implementation guidelines

1. **Minimal diffs** — Match naming, structure, and style of surrounding code. Avoid drive-by refactors.
2. **Plugin ids** — Lowercase kebab-case only. Prefer `agent-foundry create-plugin <id>` for new plugins.
3. **Registry edits** — After changing `plugins/` or `registry/plugins.yaml`, run `agent-foundry validate-plugins`.
4. **CLI/installer changes** — Add or update tests under `tests/`. Use `unittest`, not pytest.
5. **Dead code** — CI runs `vulture` at confidence 100; remove unused symbols you introduce.
6. **Secrets** — Never commit credentials, tokens, or `.env` files.
7. **Commits and PRs** — Use [Conventional Commits](https://www.conventionalcommits.org/). Fill `.github/PULL_REQUEST_TEMPLATE.md`. Do not skip hooks or required CI checks unless the user explicitly requests it.

Human contributor workflow: see `CONTRIBUTING.md`.

## Plugin layout (products under `plugins/`)

Each registry plugin typically includes:

- `.agentic/plugin.yaml` — name, version, description (must match registry entry)
- `plugin.json` and provider dirs: `.cursor-plugin/`, `.claude-plugin/`, `.codex-plugin/`
- `skills/<skill-name>/SKILL.md` — YAML frontmatter + markdown body
- `agents/<agent-name>.md` — YAML frontmatter + role/guidelines
- `commands/<name>.md` — where supported by providers
- `.mcp.json` — optional MCP server definitions

Example reference: `plugins/git/`.

## Boundaries

- **`plugins/` are end-user products** — Do not confuse them with repo dev instructions (`AGENTS.md`, `.cursor/rules/`).
- **`remove-plugin`** deletes the plugin directory and registry row in this repo only; it does not uninstall from user machines.
- **Do not modify** generated artifacts (`build/`, `agent_foundry.egg-info/`) unless fixing packaging intentionally.
- **Provider behavior** — When changing install paths or scope (`--global` vs `--in-project`), check README provider table and add tests.

## Providers quick reference

Supported `provider` values: `claude`, `codex`, `copilot`, `cursor`, `cursor-cli`.

Install kinds for granular install: `agent`, `skill`, `mcp-config`. Identifiers may use `plugin_id:resource` when ambiguous.
