# Contributing to agent-foundry

Thanks for helping improve **agent-foundry** — the CLI for installing registry-defined plugins into Codex, Claude Code, Cursor (IDE and CLI), and Copilot CLI.

## Development setup

**Requirements:** Python 3.10+

From the repository root:

```bash
pip install -e .
agent-foundry --help
```

Optional: install [pipx](https://pipx.pypa.io/) to exercise the published install path (`pipx install -e .`).

## What to contribute

| Area | Location | Notes |
| --- | --- | --- |
| Registry plugins | [`plugins/`](plugins/), [`registry/plugins.yaml`](registry/plugins.yaml) | Skills, agents, commands, MCP configs for end users |
| CLI and installers | [`agent_foundry/`](agent_foundry/) | Provider adapters, install/uninstall logic, validation |
| Tests | [`tests/`](tests/) | Unit tests; add coverage for new behavior |
| Docs | `README.md`, plugin `README.md` files | Keep usage examples in sync with the CLI |

## Adding or updating a plugin

1. **Scaffold** (recommended for new plugins):

   ```bash
   agent-foundry create-plugin <plugin_id> --version 0.1.0 --summary "Short description"
   ```

   Plugin ids must be **lowercase kebab-case** (e.g. `my-workflow`).

2. **Edit** the generated tree under `plugins/<plugin_id>/`:
   - Skills: `skills/<skill-name>/SKILL.md`
   - Agents: `agents/<agent-name>.md`
   - Commands: `commands/<command-name>.md` (where supported)
   - Provider manifests: `.cursor-plugin/`, `.claude-plugin/`, `.codex-plugin/`, `plugin.json`, etc.

3. **Register** the plugin in [`registry/plugins.yaml`](registry/plugins.yaml) if `create-plugin` did not already add an entry (it usually does).

4. **Validate** before opening a PR:

   ```bash
   agent-foundry validate-plugins
   ```

5. **Remove** a plugin from the registry (does not uninstall from user machines):

   ```bash
   agent-foundry remove-plugin <plugin_id>
   ```

See existing plugins such as [`plugins/git/`](plugins/git/) for layout and manifest patterns.

## Working on the CLI

- Entry point: [`agent_foundry/cli/app.py`](agent_foundry/cli/app.py)
- Run the full unit suite:

  ```bash
  python -m unittest discover -s tests -p "test_*.py"
  ```

- Dead-code check (CI enforces this):

  ```bash
  pip install vulture
  vulture agent_foundry tests --min-confidence 100
  ```

- Optional end-to-end smoke: [`scripts/e2e-cli.sh`](scripts/e2e-cli.sh) (see [`e2e.md`](e2e.md))

## Pull requests

1. Branch from `main` using a clear prefix, e.g. `docs/add-contributing`, `feat/my-feature`, `fix/issue-description`.
2. Keep changes focused; one logical concern per PR when possible.
3. Fill out [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md) — especially plugin/registry impact and validation checkboxes.
4. Ensure CI passes:
   - `agent-foundry validate-plugins`
   - Unit tests
   - `vulture` dead-code scan
   - Required aggregate check `required-checks`

Describe **what** changed and **why** in the PR summary. Note any security or operational risk if you touch hooks, commands, or MCP server definitions.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/) style when practical:

- `feat:` new behavior
- `fix:` bug fix
- `docs:` documentation only
- `refactor:`, `test:`, `chore:`, `ci:` as appropriate

Example: `docs: add CONTRIBUTING guide for plugins and PR workflow`

## License

By contributing, you agree that your contributions are licensed under the same terms as the project: [Apache-2.0](LICENSE).
