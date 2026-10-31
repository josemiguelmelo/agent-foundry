---
name: iac-review
description: >
  Review an infrastructure-as-code change (Terraform/OpenTofu, Pulumi, CloudFormation, Kubernetes manifests)
  for correctness, blast radius, security, and rollback safety before it is applied.
x-agent-foundry-plugin: devops
---

# Requirements

1. Repository or change reference (PR, branch, or file paths)
2. Target environment(s) and cloud/platform
3. The plan output (`terraform plan`, `pulumi preview`, `helm diff`, `kubectl diff`, or equivalent) when available

## Workflow

1. **Identify the tooling.** Read provider/module pins, backend configuration, and workspace selection to confirm which stack and state the change targets.
2. **Summarize the intent.** State in one paragraph what the change does and which environments it affects.
3. **Inspect the plan.** Group changes into `create`, `update`, `replace`, and `destroy`. Flag every replacement or destroy explicitly with its blast radius.
4. **Check state and locking.** Confirm remote state, versioning, and locking are configured. Flag local state or state-moving operations.
5. **Check security.** Review IAM/policies, network exposure (public ingress, open security groups), encryption, and secret handling. Confirm no credentials appear in code, variables, or state.
6. **Check reliability.** Verify health checks, resource limits, autoscaling bounds, multi-AZ/zone placement where required, and `lifecycle` protections for data stores.
7. **Check cost.** Call out resources with meaningful cost impact (large instances, NAT gateways, storage, egress) and whether they are intentional.
8. **Confirm the rollback.** Require an explicit rollback or forward-fix path for any irreversible change (data migration, DNS cutover, state replacement).
9. **Produce the review.** Write a structured report with a clear verdict: `approve`, `approve with changes`, or `block`.

## Output Template

```markdown
## IaC Review — <change reference>

**Verdict:** approve | approve with changes | block
**Tooling:** <tool and version> · **Environment(s):** <envs>
**Blast radius:** <resources created / updated / replaced / destroyed>

### Findings

| Severity | Resource | Finding | Recommendation |
| --- | --- | --- | --- |
| critical | | | |

### Security
- 

### Reliability and rollback
- 

### Cost
- 

### Required follow-ups
- [ ] 
```

## Rules

- Never approve a plan containing an unreviewed `replace` on a stateful resource.
- Never approve infrastructure that requires long-lived cloud credentials in the pipeline.
- If the plan is missing, request it before approving; do not infer changes from source alone.
