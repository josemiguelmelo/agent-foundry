---
name: run-software-development-agents-team
description: >
  Orchestrate the software-development-agents plugin in a repeating cycle: ask the user for the
  next step, route work to the right specialist agent (or embody that role), complete the task,
  then prompt for the next step until the user ends the session.
---

## When to use

- The user wants a **continuous, step-by-step workflow** with the plugin’s five specialists (AI, frontend, backend, architect, product manager).
- The user invokes this skill (or asks to “run the dev team loop”, “software dev agents loop”, etc.).

## Preconditions

- Workspace is the **project** where work should happen (memory and paths are per-project; see each agent file under `agents/`).
- If the user’s goal is vague, **ask concise clarifying questions** before routing or coding—do not invent scope.

## Specialist routing

Use the plugin agents as **roles** (paths are relative to the plugin folder):

| User intent (examples) | Agent file | Role |
|------------------------|------------|------|
| RAG, prompts, agent defs, skills, tools, MCP, embeddings | `agents/senior-ai-engineer.md` | Senior AI Engineer |
| React, Vite, Tailwind, browser UI, client state | `agents/senior-frontend-engineer.md` | Senior Frontend Engineer |
| APIs, DB, auth, services, integrations, ops | `agents/senior-backend-engineer.md` | Senior Backend Engineer |
| Boundaries, trade-offs, sequencing, ADRs, feasibility | `agents/senior-architect.md` | Senior Architect |
| Backlog, priorities, acceptance criteria, who does what | `agents/senior-product-manager.md` | Senior Product Manager |

**Multi-domain tasks:** Order work sensibly (e.g. architect/product clarify → backend/AI implement → frontend consume). One primary owner per chunk; hand off explicitly in your summary.

**Delegation mechanics (do not assume a single mechanism):**

- If the environment supports **subagents or task delegation**, spawn or assign the appropriate specialist for the current chunk of work.
- Otherwise, **embody** that specialist: follow the mission, scope, and collaboration rules in the matching `agents/*.md` file for this task only.

## Session loop (repeat until exit)

This is a **user-paced loop**, not a tight programmatic loop: each cycle **waits for user input** before continuing.

1. **Opening (first time in session):** Briefly state that you are running the software-development-agents team loop, list the five roles in one line, and ask: **What should we do next?**
2. **Next iterations:** After you finish the current task (see step 4), ask again: **What is the next step?** (or equivalent). Offer **2–4 short examples** of directions (e.g. “spec a feature”, “implement endpoint”, “review architecture”) only if useful—do not block on examples.
3. **Execute:** Route per the table; read the relevant `agents/*.md` and proceed. If multiple specialists are needed, sequence them and keep the user informed between chunks.
4. **Complete the step:** Summarize what was done, where artifacts live (paths), open risks, and what you recommend next (optional, non-blocking).
5. **Loop:** Return to step 2.

## Ending the loop

Stop the cycle when the user clearly ends the session, e.g. says **stop**, **done**, **exit**, **end session**, or **we’re finished**. Reply with a short closure; do not ask for another step unless they start again.

## Guardrails

- Do not claim a task is done without verifying against the user’s ask (tests, acceptance criteria, or explicit user confirmation when verification is impossible).
- Preserve **per-project memory** conventions from the agent files (e.g. `.agent-foundry/memory/software-development-agents/<agent-name>/`).
- Do not run unbounded autonomous retries; if blocked, report and ask the user.

## Output habit

Each reply after completing work should be skimmable: **Done / Not done**, **Key changes**, **Next question: What should we do next?** unless the user exited.
