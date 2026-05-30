# End-to-end CLI tests

The e2e suite exercises `agent-foundry` against real install/uninstall flows using an **isolated temporary `HOME`**. Your normal provider directories (`~/.codex`, `~/.cursor`, etc.) are not modified.

Script: [`scripts/e2e-cli.sh`](scripts/e2e-cli.sh)

## Prerequisites

- `agent-foundry` installed and on `PATH` (e.g. via [pipx](https://pipx.pypa.io/))
- `git` (required for remote `--repo` tests)
- Network access (unless using `--skip-network`)

## Running the suite

From the repository root:

```bash
chmod +x scripts/e2e-cli.sh   # once, if needed
./scripts/e2e-cli.sh
```

### Options

| Flag / variable | Description |
|-----------------|-------------|
| `USE_LOCAL_SOURCE=1` | Run the CLI from this checkout via [`scripts/run-local-cli.sh`](scripts/run-local-cli.sh) instead of the pipx-installed binary. Useful while developing without reinstalling. |
| `--skip-network` | Skip tests that clone [mattpocock/skills](https://github.com/mattpocock/skills.git). Registry and local fixture tests still run. |
| `--keep-temp` | Do not delete the temporary `HOME` and project directory after the run (for debugging). |
| `AGENT_FOUNDRY_BIN=/path/to/bin` | Use a custom CLI executable. |
| `EXTERNAL_REPO_URL=<url>` | Override the external git sample (default: `https://github.com/mattpocock/skills.git`). |

### Examples

```bash
# Full suite against pipx install
./scripts/e2e-cli.sh

# Full suite against local checkout (no pipx reinstall)
USE_LOCAL_SOURCE=1 ./scripts/e2e-cli.sh

# Offline-friendly (no remote git clone)
./scripts/e2e-cli.sh --skip-network

# Inspect temp dirs after a failure
./scripts/e2e-cli.sh --keep-temp
```

### Exit codes

- `0` — all checks passed
- `1` — one or more checks failed
- `2` — missing prerequisites or invalid script flags

On success you should see a summary like:

```text
Results: 36 passed, 0 failed (36 checks)
```

## What is tested

### Help / parser smoke

- `agent-foundry --help`
- `agent-foundry install --help`
- `agent-foundry install-plugin --help`

### Registry (local checkout)

Uses `--repo <this-checkout>` so tests do not depend on fetching GitHub.

| Use case | Command pattern | Provider |
|----------|-----------------|----------|
| Validate registry | `validate-plugins` | — |
| Full plugin install + uninstall | `install-plugin` / `uninstall-plugin` | `cursor-cli` → plugin `git` |
| Scoped skill install + uninstall | `install skill git:commit` / `uninstall skill commit` | `cursor-cli` |

Verifies skills land under `$HOME/.cursor/skills/` and are removed on uninstall.

### Local external fixture

Uses [`tests/fixtures/external-repo`](tests/fixtures/external-repo) (convention layout: `agents/`, `skills/`, `plugins/`).

| Use case | Command pattern | Notes |
|----------|-----------------|-------|
| `--path` skills override | `install skill codex commit --path skills:./alt-skills` | Skill read from non-default directory |
| Uninstall without `--path` | `uninstall skill codex commit` | Uses installed synthetic plugin id |
| Scoped plugin skill | `install skill cursor-cli my-plugin:plugin-skill` | Skill under `plugins/my-plugin/` |
| Agent install + uninstall | `install agent cursor-cli senior-reviewer` | Repo-root agent file |

### Remote external repo (mattpocock/skills)

Clones `https://github.com/mattpocock/skills.git` (or `EXTERNAL_REPO_URL`). Skills live in category subfolders, not repo-root `skills/`, so **`--path` is required** for install.

| Use case | Skill | `--path` | Provider |
|----------|-------|----------|----------|
| Nested skills path (engineering) | `tdd` | `skills:./skills/engineering` | `codex` |
| Uninstall without `--repo` / `--path` | `tdd` | — | `codex` |
| Nested skills path (productivity) | `handoff` | `skills:./skills/productivity` | `cursor-cli` |
| Uninstall | `handoff` | — | `cursor-cli` |

**Negative cases** (remote section only):

| Case | Expected exit |
|------|----------------|
| Install `tdd` without `--path` (skill not in default `skills/`) | `1` |
| Unknown skill name with valid `--path` | `1` |
| Invalid `--path` on `install-plugin` (directory missing) | `2` |

Skipped entirely when `--skip-network` is set.

### In-project scope

| Use case | Command pattern |
|----------|-----------------|
| Project-local skill install | `install skill cursor-cli my-plugin:plugin-skill --in-project` |
| Project-local uninstall | `uninstall skill cursor-cli my-plugin:plugin-skill --in-project` |

Runs inside a temporary project directory; artifacts go to `./.cursor/skills/` under that directory, not `$HOME`.

## What is not covered

- Providers other than `cursor-cli` and `codex` in install flows (claude, copilot, cursor IDE)
- `create-plugin` / `remove-plugin` (mutate the registry; not run in e2e)
- `mcp-config` install/uninstall
- `--force` (Cursor CLI agent overwrite)
- Private git credentials / SSH remotes
- Ref or tag pinning on `--repo`

## Troubleshooting

**`agent-foundry not found`**

Install the CLI or point to a binary:

```bash
pipx install git+https://github.com/josemiguelmelo/agent-foundry.git
# or, from a local checkout:
USE_LOCAL_SOURCE=1 ./scripts/e2e-cli.sh
```

**Failures on mattpocock/skills tests**

- Confirm network and `git clone` work for the URL.
- Run with `--skip-network` to isolate registry/fixture failures.
- Use `--keep-temp` and inspect paths printed at the end.

**Testing unreleased changes**

Reinstall pipx from your branch, or use:

```bash
USE_LOCAL_SOURCE=1 ./scripts/e2e-cli.sh
```
