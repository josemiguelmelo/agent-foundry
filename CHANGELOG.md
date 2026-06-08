# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0](https://github.com/josemiguelmelo/agent-foundry/compare/v1.0.0...v1.0.0) (2026-06-08)


### Features

* add release automation and CLI update notices ([#26](https://github.com/josemiguelmelo/agent-foundry/issues/26)) ([1199564](https://github.com/josemiguelmelo/agent-foundry/commit/119956462afdbf94c0997f505b35c1151bc0b34c)), closes [#25](https://github.com/josemiguelmelo/agent-foundry/issues/25)
* Add support for in-project copilot install ([#15](https://github.com/josemiguelmelo/agent-foundry/issues/15)) ([b17600d](https://github.com/josemiguelmelo/agent-foundry/commit/b17600d80326fbc3b890ecaf98c59cd8eff66dc2))
* **claude:** support --in-project via project-scoped CLI install ([#9](https://github.com/josemiguelmelo/agent-foundry/issues/9)) ([0a5924d](https://github.com/josemiguelmelo/agent-foundry/commit/0a5924df845134db0c7174cfc618d357af518754))
* **cli:** install skills, agents, and plugins from external git repos ([#21](https://github.com/josemiguelmelo/agent-foundry/issues/21)) ([3166485](https://github.com/josemiguelmelo/agent-foundry/commit/3166485d49644f9d137bc3dcfd47bee9f4fc7a6a))
* **git:** add pr-conflict-solver command skill ([#14](https://github.com/josemiguelmelo/agent-foundry/issues/14)) ([d0ff3f8](https://github.com/josemiguelmelo/agent-foundry/commit/d0ff3f8ff1c8953c14b74dfb72c675adfd59a79a))
* prefer git repository for plugin installs ([093d580](https://github.com/josemiguelmelo/agent-foundry/commit/093d580478d1e853ae7f1c46cccb6db12c74900d))
* prefer git-first plugin install source ([d5c2eca](https://github.com/josemiguelmelo/agent-foundry/commit/d5c2eca3a6c20fbc80819208f84ce7aa9e27b3ff))
* **skills:** add pr-review skill to software-development-agents ([#12](https://github.com/josemiguelmelo/agent-foundry/issues/12)) ([e8cfc51](https://github.com/josemiguelmelo/agent-foundry/commit/e8cfc51eadfec5637c4d7bfd21a12337741e37e7))
* Support install specific resource instead of full plugin ([#16](https://github.com/josemiguelmelo/agent-foundry/issues/16)) ([abb7029](https://github.com/josemiguelmelo/agent-foundry/commit/abb70293bcef0c807f441e5a39d0febcf666cc7a))


### Bug Fixes

* **cursor-cli:** fall back when .cursor-plugin manifest is missing ([#7](https://github.com/josemiguelmelo/agent-foundry/issues/7)) ([5f6691c](https://github.com/josemiguelmelo/agent-foundry/commit/5f6691c8805f4fe3e061e9e743841d77685fa062))
* **cursor-cli:** use relative in-project state paths and .agent-foundry gitignore ([#10](https://github.com/josemiguelmelo/agent-foundry/issues/10)) ([#11](https://github.com/josemiguelmelo/agent-foundry/issues/11)) ([2bcb8c8](https://github.com/josemiguelmelo/agent-foundry/commit/2bcb8c89afd61f8c281c0e6bfe72497d284fc51c))
* **cursor:** mirror skills/agents for --in-project installs ([8058be4](https://github.com/josemiguelmelo/agent-foundry/commit/8058be4f9d9264f93836d445d04735343925b18a))
* **cursor:** mirror skills/agents for --in-project installs ([cbc6302](https://github.com/josemiguelmelo/agent-foundry/commit/cbc6302525944e460d5c7b76d6f60e2cbd716311))
* Fix plugin.json ([10afab2](https://github.com/josemiguelmelo/agent-foundry/commit/10afab2f4b9b167a84c92f9eec93d2919a8feb41))


### Documentation

* add AGENTS.md and multi-tool agent instructions ([#23](https://github.com/josemiguelmelo/agent-foundry/issues/23)) ([10026e4](https://github.com/josemiguelmelo/agent-foundry/commit/10026e4331606930fde4540f1b97e533d6c7052c))
* add CONTRIBUTING guide referenced by README ([#22](https://github.com/josemiguelmelo/agent-foundry/issues/22)) ([1fe24d4](https://github.com/josemiguelmelo/agent-foundry/commit/1fe24d4d69b02e7075eadc4dbd3b3c6d9366f25a))
* add MkDocs GitHub Pages site with landing and guides ([#24](https://github.com/josemiguelmelo/agent-foundry/issues/24)) ([523d3ce](https://github.com/josemiguelmelo/agent-foundry/commit/523d3ceea6c3d29fefb584ebc2196c432da3008a))

## [Unreleased]

### Added

- GitHub Releases automation via release-please
- User and contributor documentation for staying up to date
- CLI `--version` flag and passive update notice when a newer release exists
