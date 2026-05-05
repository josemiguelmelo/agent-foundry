---
name: pr-conflict-solver
description: >
  Resolve pull request merge conflicts safely by reproducing conflicts locally, applying focused
  fixes, validating the result, and updating the source branch for re-review.
---

## When to use

- A pull request cannot be merged due to merge conflicts.
- You need a repeatable conflict-resolution flow similar to implementation workflows.
- You want to preserve both branches' intent while keeping history clean and reviewable.

## Workflow

1. Identify PR context:
   - PR number, base branch, and head branch
   - conflict files from GitHub checks or `gh pr view`
2. Sync local repository:
   - fetch latest refs
   - checkout the PR head branch
   - update base and head branches to latest remote state
3. Reproduce conflict locally:
   - merge or rebase against base (match repository policy)
   - stop at conflict markers and inspect both sides before editing
4. Resolve with intent preservation:
   - keep behavior from both sides when required
   - remove stale code paths and unused helpers introduced by conflict resolution
   - ensure no conflict markers remain
5. Validate before pushing:
   - run project tests/lint/build expected for changed scope
   - run dead-code checks if configured by the repository
6. Finalize and update PR:
   - commit conflict resolution with clear message (`fix: resolve PR conflicts for #<id>`)
   - push updated branch
   - comment on PR summarizing what was resolved and what was validated

## Guardrails

- Never use destructive git commands (`reset --hard`, force-push) unless explicitly requested.
- Do not silently drop changes from either side of the conflict.
- If conflict intent is ambiguous, stop and ask for a product/architecture decision.
- Keep conflict-resolution commits focused; avoid unrelated refactors.
- Do not include "Made with Cursor" or similar in commit messages or PR comments.

## Output format

- PR conflict diagnosis (base/head/conflict scope)
- Resolution plan (merge/rebase strategy and files to edit)
- Validation commands and outcomes
- Commit message and PR update note
