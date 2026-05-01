"""Composable validation rules for plugin bundles."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import yaml

from agent_foundry.installers import scaffold_providers
from agent_foundry.plugin.constants import (
    AGENTIC_MANIFEST_REL,
    AGENTS_DIR,
    MCP_MANIFEST_FILE,
    SKILLS_DIR,
)
from agent_foundry.plugin.types import RegistryRow, ValidationIssue
from agent_foundry.registry import RegistryPlugin, parse_plugin_row
from agent_foundry.utils.markdown import parse_frontmatter_file
from agent_foundry.utils.paths import resolve_under


def _rel(repo_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def _load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


class ValidationRule(Protocol):
    def validate(
        self, plugin: RegistryPlugin, *, context: PluginValidationContext
    ) -> list[ValidationIssue]: ...


class GlobalValidationRule(Protocol):
    def validate(self, plugins: list[RegistryPlugin]) -> list[ValidationIssue]: ...


@dataclass(frozen=True)
class PluginValidationContext:
    repo_root: Path


@dataclass(frozen=True)
class DuplicatePluginIdRule:
    def validate(self, plugins: list[RegistryPlugin]) -> list[ValidationIssue]:
        counts = Counter(p.id for p in plugins)
        return [
            ValidationIssue(f"duplicate plugin id: {plugin_id}")
            for plugin_id, count in counts.items()
            if count > 1
        ]


@dataclass(frozen=True)
class ManifestConsistencyRule:
    def validate(
        self, plugin: RegistryPlugin, *, context: PluginValidationContext
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        base = context.repo_root / plugin.path.strip()
        if not base.is_dir():
            return issues
        manifest = base / AGENTIC_MANIFEST_REL
        if not manifest.is_file():
            issues.append(
                ValidationIssue(
                    f"{plugin.id}: missing {_rel(context.repo_root, manifest)}"
                )
            )
            return issues
        try:
            data = _load_yaml(manifest)
        except Exception as exc:  # noqa: BLE001
            issues.append(
                ValidationIssue(f"{plugin.id}: invalid YAML in plugin.yaml: {exc}")
            )
            return issues
        if data.get("name") != plugin.id:
            issues.append(
                ValidationIssue(
                    f"{plugin.id}: manifest name should match id ({data.get('name')})"
                )
            )
        manifest_ver = str(data.get("version", ""))
        if manifest_ver != str(plugin.version):
            issues.append(
                ValidationIssue(
                    f"{plugin.id}: version mismatch registry={plugin.version} manifest={manifest_ver}"
                )
            )
        return issues


@dataclass(frozen=True)
class BundleStructureRule:
    def _validate_json_manifest(
        self,
        plugin_id: str,
        mpath: Path,
        base: Path,
        repo_root: Path,
        issues: list[ValidationIssue],
    ) -> None:
        if not mpath.is_file():
            return
        try:
            data = json.loads(mpath.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(
                ValidationIssue(
                    f"{plugin_id}: invalid JSON {_rel(repo_root, mpath)}: {exc}"
                )
            )
            return
        if not isinstance(data, dict):
            issues.append(
                ValidationIssue(
                    f"{plugin_id}: {_rel(repo_root, mpath)} root must be a JSON object"
                )
            )
            return
        for key in ("agents", "skills", "mcpServers", "hooks"):
            if key not in data:
                continue
            val = data[key]
            paths: list[str] = []
            if isinstance(val, str):
                paths.append(val)
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, str):
                        paths.append(item)
            for raw in paths:
                target = resolve_under(base, raw)
                if not target.exists():
                    issues.append(
                        ValidationIssue(
                            f"{plugin_id}: {_rel(repo_root, mpath)} references missing {key} path: {raw}"
                        )
                    )

    def _validate_skills_agents_disk(
        self, plugin_id: str, base: Path, issues: list[ValidationIssue]
    ) -> None:
        skills_root = base / SKILLS_DIR
        if skills_root.is_dir():
            for skill_dir in sorted(skills_root.iterdir()):
                if not skill_dir.is_dir():
                    continue
                skill_file = skill_dir / "SKILL.md"
                if not skill_file.is_file():
                    issues.append(
                        ValidationIssue(
                            f"{plugin_id}: expected {skill_file.relative_to(base)}"
                        )
                    )
                    continue
                fm = parse_frontmatter_file(skill_file)
                if not fm or not fm.get("name") or not fm.get("description"):
                    issues.append(
                        ValidationIssue(
                            f"{plugin_id}: {skill_file.relative_to(base)} needs frontmatter name + description"
                        )
                    )

        agents_dir = base / AGENTS_DIR
        if agents_dir.is_dir():
            for agent_file in sorted(agents_dir.glob("*.md")):
                fm = parse_frontmatter_file(agent_file)
                if not fm or not fm.get("name") or not fm.get("description"):
                    issues.append(
                        ValidationIssue(
                            f"{plugin_id}: {agent_file.relative_to(base)} needs frontmatter name + description"
                        )
                    )

    def validate(
        self, plugin: RegistryPlugin, *, context: PluginValidationContext
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        base = (context.repo_root / plugin.path.strip()).resolve()
        if not base.is_dir():
            issues.append(
                ValidationIssue(
                    f"{plugin.id}: plugin directory missing at {_rel(context.repo_root, base)}"
                )
            )
            return issues
        mcp = base / MCP_MANIFEST_FILE
        if not mcp.is_file():
            issues.append(ValidationIssue(f"{plugin.id}: missing {MCP_MANIFEST_FILE}"))
        else:
            try:
                json.loads(mcp.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                issues.append(ValidationIssue(f"{plugin.id}: invalid .mcp.json: {exc}"))

        self._validate_skills_agents_disk(plugin.id, base, issues)
        for provider in scaffold_providers():
            if not provider.scaffold_manifest_path:
                continue
            mpath = base / provider.scaffold_manifest_path
            self._validate_json_manifest(
                plugin.id, mpath, base, context.repo_root, issues
            )
        return issues


@dataclass(frozen=True)
class ValidatorPipeline:
    global_rules: tuple[GlobalValidationRule, ...]
    plugin_rules: tuple[ValidationRule, ...]

    def validate_all(
        self, plugins: list[RegistryPlugin], *, repo_root: Path
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        context = PluginValidationContext(repo_root=repo_root)
        for rule in self.global_rules:
            issues.extend(rule.validate(plugins))
        for plugin in plugins:
            for rule in self.plugin_rules:
                issues.extend(rule.validate(plugin, context=context))
        return issues


def parse_registry_rows(
    rows: list[RegistryRow | object],
) -> tuple[list[RegistryPlugin], list[ValidationIssue]]:
    plugins: list[RegistryPlugin] = []
    issues: list[ValidationIssue] = []
    for row in rows:
        if not isinstance(row, dict):
            issues.append(ValidationIssue("plugin entry must be a mapping"))
            continue
        if not row.get("id"):
            issues.append(ValidationIssue("plugin entry missing id"))
            continue
        parsed = parse_plugin_row(row)
        if not parsed:
            issues.append(ValidationIssue("plugin entry missing path"))
            continue
        plugins.append(parsed)
    return plugins, issues
