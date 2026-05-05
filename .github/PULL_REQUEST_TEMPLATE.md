## Summary

What does this PR change and why?

## Plugin / registry impact

- [ ] Updates `registry/plugins.yaml` or vocab files
- [ ] Adds or modifies a plugin under `plugins/`

## Validation

- [ ] `pip install -e . && agent-foundry validate-plugins`
- [ ] `pip install -e . && python -m unittest discover -s tests -p "test_*.py"`
- [ ] `pip install -e . vulture && vulture agent_foundry tests --min-confidence 100`
- [ ] GitHub required checks are all green (including `required-checks`)
- [ ] Removed dead code from this change (unused files/functions are deleted)

## Risk

Note security or operational risk if this touches `hooks/`, `commands/`, or MCP server definitions.
