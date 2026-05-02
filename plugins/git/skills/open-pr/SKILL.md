---
name: open-pr
description: >
  Open a pull request with GitHub CLI or GitLab CLI using a clear title, concise summary,
  and practical test plan derived from branch commits.
---

## When to use

- You need to open a PR/MR from the current branch.
- You want a review-friendly title/body generated from real diff and commit history.
- You need help choosing between `gh` and `glab`.

## Workflow

1. Check branch and change scope:
   - working tree status
   - commit list since base branch
   - combined diff vs base
2. Select CLI:
   - Use `gh` for GitHub remotes
   - Use `glab` for GitLab remotes
3. Draft PR title:
   - `<tag>(optional-scope): <what changed>`
   - Match dominant commit intent (`feat`, `fix`, etc.) when clear
4. Draft body (token-lean):
   - `## Summary` with 2-4 bullets
   - `## Test plan` with checklist of validations performed or needed
   - `## Notes` only if risk/migration exists
5. Ensure branch is pushed; create PR/MR with heredoc body.

## Guardrails

- Include all branch commits in the summary, not only the latest commit.
- Do not fabricate test results; mark unknown checks as TODO.
- Avoid overly long PR descriptions; prioritize reviewer clarity.
- Do not push or create PR if user has not requested execution.
- Do not include "Made with Cursor" or similar in the PR body.

## Output format

- Suggested base branch and title
- PR body draft
- Exact command(s) to run (`gh pr create` or `glab mr create`)
- PR URL after creation (if executed)
