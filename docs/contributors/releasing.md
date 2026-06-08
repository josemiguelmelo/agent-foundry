# Releasing

agent-foundry uses [release-please](https://github.com/googleapis/release-please) to automate version bumps, changelog updates, tags, and GitHub Releases.

## How it works

1. Merge feature and fix PRs to `main` with [Conventional Commit](https://www.conventionalcommits.org/) titles.
2. The [release-please workflow](https://github.com/josemiguelmelo/agent-foundry/blob/main/.github/workflows/release-please.yml) runs on each push to `main`.
3. release-please opens or updates a **Release PR** (for example, `chore(main): release 1.1.0`) that bumps `pyproject.toml` and `CHANGELOG.md`.
4. Review and merge the Release PR when you are ready to ship.
5. release-please tags `vX.Y.Z` and publishes the GitHub Release automatically.

Do **not** manually edit `pyproject.toml` version for routine releases — release-please owns it.

## Semver from commits

| Commit type | Version bump |
| --- | --- |
| `fix:` | patch |
| `feat:` | minor |
| `feat!:` or `BREAKING CHANGE:` footer | major |

`docs:`, `chore:`, `test:`, and `refactor:` commits typically do not trigger a release unless they include a recognized release trigger.

## Configuration files

| File | Purpose |
| --- | --- |
| [`release-please-config.json`](https://github.com/josemiguelmelo/agent-foundry/blob/main/release-please-config.json) | Release type (`python`), changelog path |
| [`.release-please-manifest.json`](https://github.com/josemiguelmelo/agent-foundry/blob/main/.release-please-manifest.json) | Current released version tracker |
| [`CHANGELOG.md`](https://github.com/josemiguelmelo/agent-foundry/blob/main/CHANGELOG.md) | Human-readable release history |

## First release

The manifest seeds version `1.0.0`. After enabling release-please, merge the first Release PR it opens to publish `v1.0.0`.

The `release-as: 1.0.0` setting in `release-please-config.json` forces the first release version. Remove it after the initial release so later versions follow commit semantics.

## CI on Release PRs

GitHub's default `GITHUB_TOKEN` may not re-trigger other CI workflows on release-please PRs. For this repository, manually verify Release PRs before merge. If that becomes painful, add a fine-grained PAT as a repository secret and pass it to the workflow `token` input.

## Optional announcements

For larger features, post a short note in GitHub Discussions (Announcements category) after merging a Release PR. Discussions must be enabled in repository settings.

<div class="af-related" markdown="1">

## Related

- [Contributing](contributing.md)
- [Staying up to date](../user/updates.md)
- [Releases on GitHub](https://github.com/josemiguelmelo/agent-foundry/releases)

</div>
