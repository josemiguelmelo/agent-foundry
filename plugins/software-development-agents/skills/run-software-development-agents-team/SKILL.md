---
name: run-software-development-agents-team
description: >
  Fully autonomous team loop: only user input is new tasks on the board. Fetches board, PM picks
  work and staffing (implementer + reviewer), subagents implement and another specialist reviews,
  implementer merges and closes the task, re-fetch and repeat; idle boards poll for new items.
  Board location: GitHub, Jira, or REST.
---

A **self-driving** dev loop tied to a **real task board** (GitHub, Jira, or REST). The **human** only **adds or updates items on the board**

## Preconditions

- Workspace is the **project** where work happens.

## Required input: task board location

| Source       | Collect                                                                                                                                  |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **GitHub**   | `owner/name`, Issues filters and/or **Project** (classic or v2: project id / number / owner), columns or labels meaning “ready to pull.” |
| **Jira**     | Host, project key or board id, optional **JQL** for actionable items.                                                                    |
| **REST API** | Base URL, list endpoint, pagination, **auth via env** (never paste tokens into chat).                                                    |

Use **`gh`**, Jira REST/MCP, or HTTP to **actually fetch** items—never invent lists.

## Fully autonomous loop (mandatory behavior)

Run **continuously** without waiting for user chat between tasks:

1. **Fetch** actionable tasks from the board profile. If board is empty, enter **Idle polling** mode (see below).
2. Call **senior-product-manager subagent** with the list of tasks in the board. Subagent returns **one** next task + **which specialist implements** + **which different specialist reviews** the PR (**reviewer ≠ implementer**).
3. **Delegate** implementation to subagent(s) and move task to in progress on the board; Do not add any comments on the task.
4. **Review loop (reviewer subagent only):** The **reviewer specialist subagent** (from step 2, **not** the implementer) owns the **review loop**—PR feedback, CI/review gates, and requesting changes until checks pass or **Escalation** applies. The **implementer** applies code or config fixes when the reviewer directs (re-delegate as needed). The **orchestrator does not** triage CI or review threads. Do not stop for a human to “go review” unless policy **cannot** be satisfied by bots/tools.
5. **Merge (implementer subagent only):** The **implementation specialist subagent** (same agent that implemented in step 3) runs **`gh pr merge`** (or GitLab/Jira/Azure equivalents / REST) **as soon as** branch protection and checks allow. Prefer **squash/merge** flags that match the repo. The **orchestrator does not** merge; the **reviewer does not** merge. **Do not** end the cycle with “please merge PR #n manually” as the default outcome when merge is possible with current credentials.
6. **Close / Done (implementer subagent only):** The **same implementation specialist subagent** moves the issue/task to **Done** / **Closed** / correct **Project column** using **`gh project item-edit`**, Issues API, Jira transitions, etc., immediately after merge (or define Done per automation rules). The **orchestrator does not** perform Done transitions for this task.
7. **Go back to step 1 and restart the full loop**.

**Ownership (steps 4–6):** After implementation (step 3), the orchestrator **delegates** step **4** to the **reviewer specialist** (another specialist than the implementer). It **delegates** steps **5** and **6** to the **implementation specialist**—the same subagent that built the change—who **merges** and **closes / moves to Done**.
The orchestrator **invokes** those subagents and continues the loop after they report completion; it **does not** substitute for them.

**Architect subagent:** Only when PM requests technical staffing help or task is architecture-only.

## Orchestrator is coordination only

The orchestrator does **not** choose tasks or specialists (PM subagent does). It **executes** fetches, **invokes** subagents (PM → implement → **reviewer** for step **4** → **implementer** for steps **5–6**), and **restarts the loop**.
It **does not** implement product code and **does not** own PR review, merge, or Done transitions—**review** belongs to the **reviewer specialist**; **merge** and **Done** belong to the **implementation specialist**.

## Idle polling (no tasks)

When **zero** actionable items:

- **Do not** ask the user to type **continue**.
- **Poll** the same board location on a **reasonable interval** (e.g. **3–10 minutes**, or a session-configured interval). Between polls, remain idle—no busy-tight loops.
- When **new** tasks appear, proceed automatically through **Fetch → PM → …**
- Optional: one concise status line per poll if the host supports it (“Board empty; next poll in …”)—not a blocker for human input.

Stop polling only when the user **ends the session** or a global stop condition fires.

## Specialist routing

| Role                     | Agent file                           |
| ------------------------ | ------------------------------------ |
| Senior AI Engineer       | `agents/senior-ai-engineer.md`       |
| Senior Frontend Engineer | `agents/senior-frontend-engineer.md` |
| Senior Backend Engineer  | `agents/senior-backend-engineer.md`  |
| Senior Architect         | `agents/senior-architect.md`         |
| Senior Product Manager   | `agents/senior-product-manager.md`   |

**Subagent-only:** orchestrator never implements product code.

## Guardrails

- Never skip **PM subagent** when candidates exist.
- PM must name a **reviewer specialist** distinct from the **implementation specialist** (cross-discipline review is encouraged, e.g. backend ↔ frontend).
- Never bundle unrelated board tasks into one PR without explicit batch instruction encoded **on the board** or config.
- **Secrets:** env-only auth; never echo tokens.

## Issue / work-item status

The **implementation specialist** keeps statuses truthful (**In progress** → **Done**) via API/`gh` after merge (step **6**).
