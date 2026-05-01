"""Application service for remove-plugin."""

from __future__ import annotations

from pathlib import Path

from agent_foundry.registry import RegistryRepository
from agent_foundry.plugin.operation import RemovePluginResult
from agent_foundry.utils.fsutil import unlink_or_rmtree


class RemovePluginService:
    def __init__(self, repository: RegistryRepository | None = None) -> None:
        self._repository = repository or RegistryRepository()

    def run(self, plugin_id: str) -> RemovePluginResult:
        with self._repository.session() as session:
            entry = session.get_by_id(plugin_id)
            if entry is None:
                raise ValueError(
                    f"No plugin {plugin_id!r} in {self._repository.registry_path}"
                )
            rel_raw = entry.path

            resolved = (self._repository.repo_root / Path(rel_raw.strip())).resolve()
            expected = (self._repository.repo_root / "plugins" / plugin_id).resolve()
            if resolved != expected:
                raise ValueError(
                    "Refusing to remove: registry path does not resolve to plugins/"
                    f"{plugin_id}: got {resolved} (registry path={rel_raw!r})"
                )
            session.remove(plugin_id)

        messages: list[str] = []
        resolved = (self._repository.repo_root / Path(rel_raw.strip())).resolve()
        if resolved.exists():
            unlink_or_rmtree(resolved)
            messages.append(f"Removed plugin directory {resolved}")
        else:
            messages.append(
                f"Registry updated; plugin directory already missing at {resolved}"
            )
        messages.append(f"Updated {self._repository.registry_path}")
        return RemovePluginResult(removed_dir=resolved, messages=tuple(messages))
