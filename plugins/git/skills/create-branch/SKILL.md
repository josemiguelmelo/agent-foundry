---
name: create-branch
description: >
  Create branches with consistent naming from task type and issue context, following a simple
  strategy for feature, fix, hotfix, and release flows.
---

## When to use

- You need a new working branch from a known base branch.
- You want consistent naming and issue-linked branch identifiers.
- You need to follow a lightweight branching strategy.

## Branching strategy

- `feature/`: new capabilities (base: `main` or `develop` per project convention)
- `fix/`: non-urgent bug fixes (base: active integration branch)
- `hotfix/`: urgent production fixes (base: production branch, typically `main`)
- `release/`: stabilization and release prep branches

## Naming convention

Use: `<type>/<issue-or-scope>-<short-kebab-summary>`

Examples:
- `feature/1234-user-invite-flow`
- `fix/payments-rounding-error`
- `hotfix/987-login-timeout`
- `release/1.8.0`

If an issue ID exists, include it near the start (numeric or tracker key like `PROJ-123`).

## Workflow

1. Infer task type from request (`feature`, `fix`, `hotfix`, `release`).
2. Determine correct base branch from repo strategy.
3. Generate 1-3 branch name options (short, specific, kebab-case).
4. Create branch only after confirming selected name/base when ambiguity exists.

## Guardrails

- Avoid vague names (`feature/update`, `fix/bug`).
- Keep names short (usually <= 5 words in summary segment).
- Do not branch from a dirty working tree without warning the user.
- Do not delete or rename existing branches unless requested.

## Output format

- Recommended base branch
- Recommended branch name options
- Selected branch creation command
- Confirmation of current checked-out branch (if executed)
