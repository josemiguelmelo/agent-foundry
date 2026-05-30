# agent-foundry

[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://josemiguelmelo.github.io/agent-foundry/)

`agent-foundry` is a CLI for installing registry-defined plugins into Codex, Claude Code, Cursor (IDE and CLI), and Copilot CLI.

**Full documentation:** [josemiguelmelo.github.io/agent-foundry](https://josemiguelmelo.github.io/agent-foundry/)

## Quick install

**Prerequisites:** Python 3.10+, [pipx](https://pipx.pypa.io/)

```bash
pipx install git+https://github.com/josemiguelmelo/agent-foundry.git
```

## Quick example

```bash
# Install the git workflow plugin for Cursor CLI
agent-foundry install-plugin cursor-cli git

# Install one skill into the current project
agent-foundry install skill cursor-cli git:commit --in-project
```

Plugins are indexed in [`registry/plugins.yaml`](registry/plugins.yaml). See the [plugin catalog](https://josemiguelmelo.github.io/agent-foundry/plugins/) for available bundles.

## Documentation

| Topic | Link |
| --- | --- |
| Getting started | [docs](https://josemiguelmelo.github.io/agent-foundry/user/getting-started/) |
| CLI reference | [docs](https://josemiguelmelo.github.io/agent-foundry/user/cli-reference/) |
| Providers & scope | [docs](https://josemiguelmelo.github.io/agent-foundry/user/providers/) |
| External repositories | [docs](https://josemiguelmelo.github.io/agent-foundry/user/external-repos/) |
| Plugin catalog | [docs](https://josemiguelmelo.github.io/agent-foundry/plugins/) |
| Contributing | [docs](https://josemiguelmelo.github.io/agent-foundry/contributors/contributing/) |

## Contribution

See [`CONTRIBUTING.md`](CONTRIBUTING.md). AI agents: see [`AGENTS.md`](AGENTS.md).

Licensed under Apache-2.0 — [`LICENSE`](LICENSE).
