"""Application service for validate-plugins."""

from __future__ import annotations

from agent_foundry.registry import RegistryRepository
from agent_foundry.plugin.operation import ValidatePluginsResult
from agent_foundry.plugin.validation.rules import (
    BundleStructureRule,
    DuplicatePluginIdRule,
    ManifestConsistencyRule,
    ValidatorPipeline,
    parse_registry_rows,
)


class ValidatePluginsService:
    def __init__(self, repository: RegistryRepository | None = None) -> None:
        self._repository = repository or RegistryRepository()
        self._pipeline = ValidatorPipeline(
            global_rules=(DuplicatePluginIdRule(),),
            plugin_rules=(ManifestConsistencyRule(), BundleStructureRule()),
        )

    def run(self) -> ValidatePluginsResult:
        with self._repository.session() as session:
            plugins, issues = parse_registry_rows(session.rows)
            issues.extend(
                self._pipeline.validate_all(
                    plugins, repo_root=self._repository.repo_root
                )
            )
        if issues:
            return ValidatePluginsResult(
                exit_code=1,
                messages=("Validation failed:",),
                issue_messages=tuple(f"  - {issue.message}" for issue in issues),
            )
        return ValidatePluginsResult(
            exit_code=0,
            messages=(f"OK: {len(plugins)} plugins",),
        )
