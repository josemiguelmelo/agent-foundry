# Plugin Development

This guide covers how to create and maintain registry plugins under `plugins/`.

## Plugin layout

Each registry plugin typically includes:

- `.agentic/plugin.yaml` — name, version, description (must match registry entry)
- `plugin.json` and provider dirs: `.cursor-plugin/`, `.claude-plugin/`, `.codex-plugin/`
- `skills/<skill-name>/SKILL.md` — YAML frontmatter + markdown body
- `agents/<agent-name>.md` — YAML frontmatter + role/guidelines
- `commands/<name>.md` — where supported by providers
- `.mcp.json` — optional MCP server definitions

Example reference: `plugins/git/`.

## Scaffold a new plugin

```bash
agent-foundry create-plugin <plugin_id> --version 0.1.0 --summary "Short description"
```

Plugin ids must be **lowercase kebab-case** only (e.g. `my-workflow`).

The command creates the directory tree under `plugins/<plugin_id>/` and appends an entry to `registry/plugins.yaml`.

## Registry entry

Each plugin is indexed in `registry/plugins.yaml`:

```yaml
plugins:
  - id: my-plugin
    path: plugins/my-plugin
    version: 0.1.0
    summary: Short description shown in the catalog
```

Manifest `name` and `version` in `.agentic/plugin.yaml` and provider manifests must match the registry entry. CI validates this with `validate-plugins`.

## Skills

Skills live in `skills/<skill-name>/SKILL.md`:

```
skills/
  my-skill/
    SKILL.md
```

Each `SKILL.md` file uses YAML frontmatter followed by markdown instructions.

## Agents

Agents are single markdown files in `agents/`:

```
agents/
  my-agent.md
```

Each file uses YAML frontmatter with role and guidelines.

## Commands

Commands are supported on some providers:

```
commands/
  my-command.md
```

## Provider manifests

Each plugin includes provider-specific manifest files so the CLI knows how to install content:

| Provider | Manifest location |
| --- | --- |
| Cursor | `.cursor-plugin/plugin.json` |
| Claude Code | `.claude-plugin/plugin.json` |
| OpenAI Codex | `.codex-plugin/plugin.json` |
| GitHub Copilot CLI | `plugin.json` |
| Registry / CI | `.agentic/plugin.yaml` |

## Validation

Always validate before opening a PR:

```bash
agent-foundry validate-plugins
```

Validation checks:

- Duplicate plugin ids
- Manifest name/version consistency with registry
- Bundle structure (required directories and files)
- Skill and agent frontmatter

## Remove a plugin

```bash
agent-foundry remove-plugin <plugin_id>
```

This deletes `plugins/<plugin_id>/` and its registry entry in **this repository only**. It does not uninstall from user machines.

## Boundaries

- **`plugins/` are end-user products** — do not confuse them with repo dev instructions (`AGENTS.md`, `.cursor/rules/`).
- **Provider behavior** — when changing install paths or scope (`--global` vs `--in-project`), update docs and add tests.
- **Do not modify** generated artifacts (`build/`, `agent_foundry.egg-info/`) unless fixing packaging intentionally.

<div class="af-related" markdown="1">

## Related

- [Contributing](contributing.md)
- [Plugin catalog](../plugins/index.md)
- [Architecture](architecture.md)
- [Source path overrides](../user/source-paths.md)

</div>
