---
name: fastify-handler-review
description: >
  Review Fastify routes and plugins for schema validation, auth boundaries, error mapping,
  and async safety. Use when auditing or polishing TypeScript backend PRs.
---

## When to use

- A PR touches Fastify route registration, `preHandler` chains, or reply serialization
- You need a consistent pass for status codes, validation, and leaking internals in errors

## Workflow

1. Map each route to its schema (body/query/params/response) and auth hook.
2. Flag missing or loose JSON Schema / TypeBox / Zod alignment with Fastify’s serializer.
3. Check **authZ** on resource ids (no IDOR); confirm destructive methods are protected.
4. Note **async** footguns: unhandled rejections, missing `await` on promises returned to reply.
5. Summarize **blocker / should-fix / nit** with file and route reference.

## Guardrails

- Do not suggest `force-unlock` or destructive production commands without explicit owner context.
- Treat logs and error payloads as potentially sensitive; avoid recommending verbose stack traces to clients in production.

## Examples

**Finding:** `POST /invoices` accepts `amount` as string with no `minimum`/numeric schema → add typed schema and 400 on invalid input.
