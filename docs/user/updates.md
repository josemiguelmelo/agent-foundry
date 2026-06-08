# Staying up to date

agent-foundry ships new features and fixes through [GitHub Releases](https://github.com/josemiguelmelo/agent-foundry/releases). This page explains how to hear about updates and upgrade the CLI.

## Subscribe to release notifications

The most reliable way to get notified is to watch the repository on GitHub:

1. Open [josemiguelmelo/agent-foundry](https://github.com/josemiguelmelo/agent-foundry).
2. Click **Watch** → **Custom**.
3. Enable **Releases** only.

You will receive GitHub notifications when a new release is published.

## Upgrade the CLI

If you installed with pipx (recommended):

```bash
pipx upgrade agent-foundry
```

To install a specific release tag:

```bash
pipx install --force git+https://github.com/josemiguelmelo/agent-foundry.git@v1.0.0
```

Replace `v1.0.0` with the version shown on the [Releases](https://github.com/josemiguelmelo/agent-foundry/releases) page.

Check your installed version:

```bash
agent-foundry --version
```

## CLI update notice

When you run a subcommand, agent-foundry may print a one-line hint on stderr if a newer GitHub release exists. The notice appears at most once per new release version.

Disable the check:

```bash
export AGENT_FOUNDRY_NO_UPDATE_CHECK=1
```

The check uses the public GitHub API and fails silently when offline or when no releases exist yet.

## Optional: GitHub Discussions

If repository Discussions are enabled, maintainers may post feature announcements in an **Announcements** category. Subscribe to that category for broader updates beyond release notes.

<div class="af-related" markdown="1">

## Related

- [Installation](installation.md)
- [CLI reference](cli-reference.md)
- [Releases on GitHub](https://github.com/josemiguelmelo/agent-foundry/releases)

</div>
