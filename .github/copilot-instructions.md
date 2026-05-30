# agent-foundry — Copilot instructions

CLI for installing registry-defined plugins into Codex, Claude Code, Cursor, and Copilot CLI.

**Full agent guide:** [AGENTS.md](../AGENTS.md) at the repository root.

## Commands (run before PR)

```bash
pip install -e .
agent-foundry validate-plugins
python -m unittest discover -s tests -p "test_*.py"
vulture agent_foundry tests --min-confidence 100
```

## PR checklist

- Fill `.github/PULL_REQUEST_TEMPLATE.md`
- Plugin/registry changes: run `validate-plugins`
- CLI changes: add `unittest` coverage
- Conventional Commits; focused diffs; no secrets

Path-specific rules: `.github/instructions/*.instructions.md`
