"""Application service for create-plugin."""

from __future__ import annotations

from agent_foundry.registry import RegistryPlugin, RegistryRepository
from agent_foundry.plugin.crud.scaffold import write_base_scaffold
from agent_foundry.plugin.operation import CreatePluginResult
from agent_foundry.plugin.types import Plugin, PluginSpec


class CreatePluginService:
    def __init__(self, repository: RegistryRepository | None = None) -> None:
        self._repository = repository or RegistryRepository()

    def run(
        self, plugin_id: str, *, version: str = "0.1.0", summary: str | None = None
    ) -> CreatePluginResult:
        Plugin.validate_id(plugin_id)
        desc = summary or f"TODO: describe the {plugin_id} plugin."
        spec = PluginSpec(
            id=plugin_id,
            version=version,
            summary=desc,
            repo_root=self._repository.repo_root,
        )

        with self._repository.session() as session:
            if session.get_by_id(plugin_id):
                raise ValueError(
                    f"Plugin id {plugin_id!r} is already listed in {self._repository.registry_path}"
                )
            if spec.plugin_dir.exists():
                raise FileExistsError(
                    f"Refusing to create plugin {plugin_id!r}: path already exists: {spec.plugin_dir}"
                )

            write_base_scaffold(spec)
            session.append(
                RegistryPlugin(
                    id=plugin_id,
                    path=f"plugins/{plugin_id}",
                    version=version,
                    summary=desc,
                )
            )
        return CreatePluginResult(
            plugin_dir=spec.plugin_dir,
            messages=(
                f"Created plugin at {spec.plugin_dir}",
                f"Updated {self._repository.registry_path}",
            ),
        )
