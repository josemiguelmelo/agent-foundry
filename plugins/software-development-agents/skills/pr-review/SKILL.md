---
name: pr-review
description: >
  Analyze a Pull Request, review code quality and architecture, detect potential issues or duplicated logic,
  and generate a structured review report with suggested improvements.
x-agent-foundry-plugin: software-development-agents
---

# Requirements

1. PR id
2. Repo URL

## Workflow

1. Fetch the PR to get the target branch.
2. Call senior-pull-request-reviewer agent with PR details (repo URL, PR branch, target branch).
