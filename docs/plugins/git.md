# git

Git workflow plugin for branch creation, commit quality, PR opening, and conflict resolution.

| Field | Value |
| --- | --- |
| **Plugin id** | `git` |
| **Version** | 0.1.0 |
| **Path** | `plugins/git` |

!!! example "Quick install"
    ```bash
    agent-foundry install-plugin cursor-cli git
    ```

## Install

```bash
agent-foundry install-plugin <provider> git
```

Install individual skills:

```bash
agent-foundry install skill cursor-cli git:commit
agent-foundry install skill cursor-cli git:create-branch
agent-foundry install skill cursor-cli git:open-pr
agent-foundry install skill cursor-cli git:pr-conflict-solver
```

## Skills

| Skill | Description |
| --- | --- |
| `create-branch` | Recommends and creates branch names using `feature/`, `fix/`, `hotfix/`, `release/` strategy |
| `commit` | Prepares high-quality conventional commits with concise intent-focused messages |
| `open-pr` | Drafts and opens PRs/MRs via `gh` or `glab` with clear title, summary, and test plan |
| `pr-conflict-solver` | Resolves pull request merge conflicts with a safe local workflow and validation gate |

## Validation

From the repository root:

```bash
agent-foundry validate-plugins
```

<div class="af-related" markdown="1">

## Related

- [Plugin catalog](index.md)
- [Installation](../user/installation.md)

</div>
