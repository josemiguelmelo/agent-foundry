"""Repository and session primitives for ``registry/plugins.yaml``."""

from __future__ import annotations

from contextlib import AbstractContextManager
from dataclasses import asdict
from pathlib import Path

from agent_foundry.registry.core import RegistryPlugin, find_registry_file, parse_plugin_row
from agent_foundry.registry.document import load_document, plugins_list_mut, save_document
from agent_foundry.registry.core import repository_root


class RegistrySession(AbstractContextManager["RegistrySession"]):
    def __init__(self, repository: RegistryRepository) -> None:
        self._repository = repository
        self._data = load_document(repository.registry_path)
        self._rows = plugins_list_mut(self._data)
        self._dirty = False

    @property
    def rows(self) -> list[object]:
        return self._rows

    def plugins(self) -> list[RegistryPlugin]:
        out: list[RegistryPlugin] = []
        for row in self._rows:
            plugin = parse_plugin_row(row)
            if plugin:
                out.append(plugin)
        return out

    def get_by_id(self, plugin_id: str) -> RegistryPlugin | None:
        for plugin in self.plugins():
            if plugin.id == plugin_id:
                return plugin
        return None

    def append(self, plugin: RegistryPlugin) -> None:
        self._rows.append(asdict(plugin))
        self._dirty = True

    def remove(self, plugin_id: str) -> RegistryPlugin:
        for idx, row in enumerate(self._rows):
            plugin = parse_plugin_row(row)
            if plugin and plugin.id == plugin_id:
                self._rows.pop(idx)
                self._dirty = True
                return plugin
        raise ValueError(f"No plugin {plugin_id!r} in {self._repository.registry_path}")

    def commit(self) -> None:
        if self._dirty:
            save_document(self._repository.registry_path, self._data)
            self._dirty = False

    def __exit__(self, exc_type, exc, _exc_tb) -> bool | None:
        if exc_type is None:
            self.commit()
        return None


class RegistryRepository:
    def __init__(self, registry_path: Path | None = None) -> None:
        self._registry_path = registry_path or find_registry_file()
        self._repo_root = repository_root(self._registry_path)

    @property
    def registry_path(self) -> Path:
        return self._registry_path

    @property
    def repo_root(self) -> Path:
        return self._repo_root

    def load_plugins(self) -> list[RegistryPlugin]:
        with self.session() as session:
            return session.plugins()

    def load_rows(self) -> list[object]:
        data = load_document(self._registry_path)
        return plugins_list_mut(data)

    def get_by_id(self, plugin_id: str) -> RegistryPlugin | None:
        with self.session() as session:
            return session.get_by_id(plugin_id)

    def append(self, plugin: RegistryPlugin) -> None:
        with self.session() as session:
            session.append(plugin)

    def remove(self, plugin_id: str) -> RegistryPlugin:
        with self.session() as session:
            return session.remove(plugin_id)

    def session(self) -> RegistrySession:
        return RegistrySession(self)
