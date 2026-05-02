---
name: create-issue
description: >
  Create an issue using a fixed markdown template (description body), then open it on GitHub via
  gh (optional GitHub Project), GitLab via glab, or Jira via MCP tools only if a Jira MCP server is
  available.
---

## When to use

- The user wants a **tracked issue** created with consistent structure, not only a draft.
- Target is one of: **GitHub** (CLI + optional Project), **GitLab** (CLI), or **Jira** (MCP).

## Target system (pick one per run)

1. If the user names the system (`GitHub`, `GitLab`, `Jira`), use that.
2. Otherwise infer from `git remote get-url origin`:
   - `github.com` → GitHub
   - `gitlab.com` or self-hosted GitLab remote → GitLab
3. If inference fails, **ask** which system before creating anything.

## Required inputs (ask if missing)

1. **Title** — short, imperative.
2. **Type** — `feature`, `bug`, `task`, `spike`, or `chore` (map loose wording).
3. **Summary** / **Problem** — per template below.
4. **Acceptance criteria** — at least one testable item.

Plus **target-specific** requirements:

| System | Extra                                                                                                                                 |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| GitHub | Repo (`owner/name`) if not obvious from context; optional **GitHub Project** id/number + owner (org or user) for `gh project` linkage |
| GitLab | Path or group/project if not inferred from remote                                                                                     |
| Jira   | **Project key** (e.g. `PROJ`), **issue type** (Task/Bug/Story, …) per instance                                                        |

## Issue body template (must follow)

Build the issue **description** from this markdown template (exact section titles and order). Drop optional sections if empty (remove the section, no “N/A” filler unless the user wants a full skeleton).

```markdown
# <title>

## Metadata

| Field    | Value                                      |
| -------- | ------------------------------------------ |
| Type     | <feature \| bug \| task \| spike \| chore> |
| Priority | <e.g. P1 / Unknown>                        |
| Estimate | <e.g. S / M / L / Unknown>                 |

## Summary

…

## Problem

<!-- Bugs or motivation; omit section if not applicable. -->

…

## Goals

- …

## Context

…

## Scope

### In scope

- …

### Out of scope

- …

## Acceptance criteria

- [ ] …

## Technical notes

<!-- Omit section if empty. -->

…

## Dependencies

<!-- Omit section if empty. -->

…
```

Save the filled template (minus the leading `# <title>` duplicate if the CLI sets title separately) as the **body**: use the full template including `# <title>` only when the tracker keeps title inside the body; for `gh`/`glab`, pass **title** via CLI flags and use the template **without** the top `#` line **or** include it in the body—**prefer** title in CLI + body without redundant H1 if it duplicates the title field.

**Recommendation:** CLI `--title` = same string as `<title>` in template; **body** starts at `## Metadata` through end (or include `# title` once in body only if the team wants it—stay consistent per repo).

## Workflow

1. Gather inputs and build the markdown body (file or here-doc).
2. Route by target:

### A. GitHub (`gh`)

**Preconditions**

- `gh` is installed (`gh --version`).
- Authenticated (`gh auth status`). If not, tell the user to run `gh auth login`—do not bypass.

**Create issue**

- Default repo from `gh repo view --json nameWithOwner -q .nameWithOwner` or parse remote; allow `--repo OWNER/REPO` when the user specifies another repo.
- Prefer a temp file for the body to avoid shell escaping issues:

  ```bash
  gh issue create --repo OWNER/REPO --title "TITLE" --body-file /path/to/body.md
  ```

- Capture the **issue URL** from command output.

**GitHub Project (optional)**

- Only if the user asked to add the issue to a **GitHub Project** (new Projects).
- Requires knowing **owner** (org or user) and **project number** (or discover via `gh project list --owner OWNER`).
- After the issue exists, link it with the issue URL:

  ```bash
  gh project item-add <project-number> --owner OWNER --url <issue-url>
  ```

  Use `gh project --help` / `gh project item-add --help` for the exact flags supported by the installed `gh` version. If linking fails, report the issue URL and the project linkage error; do not claim project linkage succeeded.

### B. GitLab (`glab`)

**Preconditions**

- `glab` is installed (`glab --version`).
- Authenticated (`glab auth status` or equivalent). If not configured, instruct the user to authenticate—do not invent tokens.

**Create issue**

- Resolve project from context (`glab repo view` / remote) or `--repo GROUP/PROJECT` per `glab issue create --help`.

- There is typically **no** `--description-file` flag; pass the body explicitly:

  ```bash
  glab issue create --title "TITLE" --description "$(cat /path/to/body.md)"
  ```

  If quoting breaks on multi-line content, use the shell or runner’s supported pattern (stdin/heredoc) per `glab issue create --help` for your version—avoid mangling markdown tables.

- Return the issue URL from CLI output when present.

### C. Jira (MCP only)

**Preconditions**

- A **Jira MCP server** must be configured and visible to this session (tools/resources that create or manage Jira issues).

**If no Jira MCP tools are available**

- **Stop.** Respond clearly: Jira creation requires a configured Jira MCP server; do not simulate creation or paste fake ticket keys.

**If Jira MCP is present**

- Use the MCP tools exposed by that server to **create** an issue with:
  - **Project key** and **issue type** from the user.
  - **Summary** = title.
  - **Description** = the markdown body (or the format the MCP/API requires—if the tool expects ADF or plain text, convert minimally and note any formatting loss).

- Map **labels**, **priority**, or **components** only when the tool supports them and the user supplied values.

- Return the **canonical issue key and URL** from the tool response.

## Deliverable (after successful creation)

- Confirm **system** (GitHub / GitLab / Jira).
- Paste **URL** (and **issue number/key**).
- If GitHub Project was requested, confirm whether **project linkage** succeeded.
- Optionally append the **markdown body** used (for audit) unless the user asked not to clutter.

## Guardrails

- Never pass secrets into issue text; never echo tokens.
- Do not claim success if the CLI or MCP returned an error—surface stderr / tool error.
- Do not fall back from Jira to “markdown only” unless the user explicitly asks for a draft after MCP is missing.
