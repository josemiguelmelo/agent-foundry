---
name: ci-cd-pipeline
description: >
  Design or update a CI/CD pipeline with fast feedback, least-privilege credentials,
  quality gates, immutable artifacts, and a safe rollback path.
x-agent-foundry-plugin: devops
---

# Requirements

1. CI/CD platform (e.g., GitHub Actions, GitLab CI, CircleCI, Argo CD)
2. Repository language/toolchain and existing pipeline files
3. Target environments and promotion order (e.g., dev → staging → production)

## Workflow

1. **Audit the current pipeline.** Read every workflow/config file. Note duplicated jobs, unpinned actions, hidden required checks, and slow steps.
2. **Define stages.** Order: `lint` → `test` → `build` → `scan` → `publish` → `deploy <env>`. Each stage must fail loudly and stop promotion.
3. **Make credentials safe.** Prefer OIDC/short-lived tokens. Scope permissions per job (`permissions:` block in GitHub Actions). Remove long-lived cloud keys and over-broad tokens.
4. **Pin and cache.** Pin action/tool versions to immutable refs. Add dependency and build-layer caching keyed on lockfiles, with a fallback path when the cache is cold.
5. **Build once, promote many.** Produce an immutable, versioned artifact (image digest, tarball, or package) in `build` and deploy that exact artifact through environments. Never rebuild per environment.
6. **Add gates.** Required checks: tests, type-check/lint, dependency and container scanning, and IaC plan review for infrastructure changes. Production deploys require environment approval.
7. **Define rollback.** Document and automate the rollback command or previous-artifact promotion. Verify the pipeline can redeploy the last known good version.
8. **Validate locally.** Lint the workflow syntax (e.g., `actionlint`, `gitlab-ci-lint`) and dry-run where the platform supports it.
9. **Ship and observe.** After the first run, confirm stage timings and failure messages are actionable.

## Output Template

```markdown
## Pipeline Plan — <repo>

**Platform:** <platform> · **Artifact:** <image/tag/package>
**Environments:** dev → staging → production

| Stage | Jobs | Gate | Est. duration |
| --- | --- | --- | --- |
| lint | | required | |
| test | | required | |
| build | | required | |
| scan | | required | |
| deploy | | approval (prod) | |

### Credentials and permissions
- 

### Caching
- 

### Rollback
- 
```

## Rules

- No `latest` tags for actions, tools, base images, or artifacts that reach production.
- No secrets in workflow files or logs; mask anything derived from them.
- Pipeline changes must be reviewable in a single PR with the expected check names documented.
