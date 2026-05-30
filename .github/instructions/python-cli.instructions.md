---
applyTo: "agent_foundry/**,tests/**"
---

# Python CLI and tests

See [AGENTS.md](../../AGENTS.md) for architecture and validation commands.

- Extend providers in `agent_foundry/installers/*_provider.py`
- Add CLI handlers under `agent_foundry/cli/handlers/`
- Use `unittest`; fixtures in `tests/fixtures/`
- Run `vulture agent_foundry tests --min-confidence 100` before PR
- Match existing code style; avoid unnecessary abstractions
