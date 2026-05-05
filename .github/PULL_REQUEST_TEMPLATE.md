## Summary

What does this PR change and why?

## Plugin / registry impact

- [ ] Updates `registry/plugins.yaml` or vocab files
- [ ] Adds or modifies a plugin under `plugins/`

## Validation

- [ ] `pip install -e . && agent-foundry validate-plugins`
- [ ] `pip install -e . && python -m unittest discover -s tests -p "test_*.py"`
- [ ] GitHub required checks are all green (including `required-checks`)

## Risk

Note security or operational risk if this touches `hooks/`, `commands/`, or MCP server definitions.
