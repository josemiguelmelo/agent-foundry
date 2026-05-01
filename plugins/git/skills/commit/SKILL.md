---
name: commit
description: >
  Create high-quality git commits using Conventional Commit tags and concise, intent-focused
  messages based on staged and unstaged changes.
---

## When to use

- You need to create one or more commits from local changes.
- You want consistent commit tags (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`, `revert`).
- You want a concise message that explains why the change exists.

## Workflow

1. Inspect repo state (`git status`, staged and unstaged diff, recent commit style).
2. Group related file changes into a single logical commit; keep unrelated changes out.
3. Choose the best tag:
   - `feat`: new behavior
   - `fix`: bug correction
   - `refactor`: internal structure change without behavior change
   - `docs`: documentation only
   - `test`: tests only
   - `chore`: maintenance/housekeeping
   - `perf`, `ci`, `build`, `revert` as applicable
4. Draft message format:
   - Subject: `<tag>(optional-scope): <short imperative summary>`
   - Body: 1-2 short lines on motivation/impact when needed
5. Commit only when requested by the user; never include secrets.

## Guardrails

- Never commit `.env`, keys, or credentials unless explicitly requested and acknowledged.
- Never amend/rewrite history unless explicitly requested.
- If hooks fail, fix and create a new commit rather than force-skipping checks.
- Prefer small focused commits over large mixed commits.

## Output format

- Proposed commit grouping (files per commit)
- Proposed message(s)
- Risks or ambiguities (if any)
- Executed commands and result (if execution is requested)
