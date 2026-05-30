# Architecture

This page describes the internal architecture of the **agent-foundry** CLI and repository.

## Overview

**agent-foundry** is a Python CLI that installs registry-defined plugins into Claude Code, Codex, Copilot CLI, Cursor IDE, and Cursor CLI.

Plugins live under `plugins/` and are indexed in `registry/plugins.yaml`. End users install bundles; this repository also contains the CLI implementation and validation logic.

## Data flow

```text
registry/plugins.yaml  →  RegistryRepository
                              ↓
plugins/<id>/          →  validate-plugins (ManifestConsistency, BundleStructure)
                              ↓
agent_foundry/installers/*_provider.py  →  install-plugin / install / uninstall
```

## Repository: `validate-plugins`

The `validate-plugins` command checks registry and manifest consistency before install:

1. Load `registry/plugins.yaml` via `RegistryRepository`
2. For each plugin under `plugins/<id>/`, run validation rules:
   - **ManifestConsistency** — manifest `name`/`version` must match registry
   - **BundleStructure** — required directories and files exist
   - Skill/agent frontmatter checks
3. Exit non-zero on any failure

Run from the repository root after changing plugins or the registry.

## Install: `install-plugin` / `install`

Install commands resolve the source repository, locate plugin or item content, and delegate to a provider-specific installer:

1. **Resolve source** — default GitHub fetch, `--repo` override, or local discovery
2. **Locate content** — registry lookup or external repo layout (`agents/`, `skills/`, `plugins/`)
3. **Apply path overrides** — optional `--path <kind>:<dir>` for non-standard layouts
4. **Provider install** — copy or symlink files to provider-specific discovery paths
5. **Track state** — record install destinations for uninstall (under `.agent-foundry/`)

Uninstall reverses tracked destinations; it does not require `--path`.

## Repository map

| Path | Purpose |
| --- | --- |
| `agent_foundry/` | CLI entrypoint, registry loading, per-provider installers, plugin validation and scaffolding |
| `plugins/` | Distributable plugin bundles (skills, agents, commands, MCP configs) |
| `registry/plugins.yaml` | Central plugin index (id, path, version, summary) |
| `tests/` | Unit tests (`unittest`) |
| `scripts/e2e-cli.sh`, `e2e.md` | Optional manual end-to-end smoke tests |
| `pyproject.toml` | Package metadata and `agent-foundry` console script |
| `docs/` | MkDocs documentation site (this site) |

Do not treat `build/`, `*.egg-info/`, or local install state under `~/.agent-foundry/` as source of truth.

## Key modules

| Module | Responsibility |
| --- | --- |
| `agent_foundry/cli/app.py` | argparse wiring; subcommands: `install-plugin`, `install`, `uninstall`, `validate-plugins`, `create-plugin`, `remove-plugin` |
| `agent_foundry/registry/` | Loads and parses `registry/plugins.yaml`; external repo layout in `external.py` |
| `agent_foundry/installers/` | One module per provider (`cursor_provider.py`, `cursor_cli_provider.py`, `claude_provider.py`, `codex_provider.py`, `copilot_provider.py`); shared selection and source-path logic |
| `agent_foundry/plugin/validation/rules.py` | Duplicate plugin ids; manifest consistency; bundle structure; skill/agent frontmatter |
| `agent_foundry/plugin/crud/` | `create-plugin` scaffold, `remove-plugin` |

## Cursor CLI install behavior

Cursor CLI install mirrors plugin skills to `.cursor/skills/<name>/` and agents to `.cursor/agents/`, with state under `.agent-foundry/cursor-cli/`.

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

## Implementation guidelines

1. **Minimal diffs** — match naming, structure, and style of surrounding code
2. **Plugin ids** — lowercase kebab-case only; prefer `agent-foundry create-plugin <id>`
3. **Registry edits** — after changing `plugins/` or `registry/plugins.yaml`, run `validate-plugins`
4. **CLI/installer changes** — add or update tests under `tests/` (use `unittest`, not pytest)
5. **Dead code** — CI runs `vulture` at confidence 100
6. **Secrets** — never commit credentials, tokens, or `.env` files

## Providers quick reference

Supported `provider` values: `claude`, `codex`, `copilot`, `cursor`, `cursor-cli`.

Install kinds for granular install: `agent`, `skill`, `mcp-config`. Identifiers may use `plugin_id:resource` when ambiguous.

<div class="af-related" markdown="1">

## Related

- [Contributing](contributing.md)
- [Plugin development](plugin-development.md)
- [CLI reference](../user/cli-reference.md)

</div>
