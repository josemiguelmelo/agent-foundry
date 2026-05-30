from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agent_foundry.core.errors import UsageError
from agent_foundry.installers.source_paths import (
    apply_source_path_overrides,
    load_effective_manifest,
    parse_path_overrides,
    prepared_plugin_for_install,
    validate_override_paths,
)
from agent_foundry.installers.specific import materialized_specific_plugin
from agent_foundry.installers.selection import synthetic_plugin_id_for_uninstall
from agent_foundry.registry.external import resolve_external_specific_selection

FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "external-repo"


class TestParsePathOverrides(unittest.TestCase):
    def test_none_when_empty(self) -> None:
        self.assertIsNone(parse_path_overrides(None))
        self.assertIsNone(parse_path_overrides([]))

    def test_parses_kind_aliases(self) -> None:
        out = parse_path_overrides(["skills:./vendor/skills", "agent:./vendor/agents"])
        self.assertEqual(out, {"skills": ["./vendor/skills"], "agents": ["./vendor/agents"]})

    def test_appends_same_kind(self) -> None:
        out = parse_path_overrides(["skills:./a", "skills:./b"])
        self.assertEqual(out, {"skills": ["./a", "./b"]})

    def test_rejects_missing_colon(self) -> None:
        with self.assertRaises(UsageError):
            parse_path_overrides(["skills"])

    def test_rejects_unknown_kind(self) -> None:
        with self.assertRaises(UsageError):
            parse_path_overrides(["widgets:./x"])


class TestApplySourcePathOverrides(unittest.TestCase):
    def test_replaces_manifest_keys(self) -> None:
        root = Path("/tmp/plugin")
        manifest = {"skills": "./skills", "agents": "./agents"}
        patched = apply_source_path_overrides(
            manifest, {"skills": ["./vendor/skills"]}, plugin_root=root
        )
        self.assertEqual(patched["skills"], "./vendor/skills")
        self.assertEqual(patched["agents"], "./agents")

    def test_multiple_roots_become_list(self) -> None:
        root = Path("/tmp/plugin")
        manifest = {"skills": "./skills"}
        patched = apply_source_path_overrides(
            manifest, {"skills": ["./a", "./b"]}, plugin_root=root
        )
        self.assertEqual(patched["skills"], ["./a", "./b"])


class TestPreparedPluginForInstall(unittest.TestCase):
    def test_patches_manifest_in_temp_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "demo-plugin"
            skills = root / "custom-skills" / "demo-skill"
            skills.mkdir(parents=True)
            (skills / "SKILL.md").write_text("# Demo\n", encoding="utf-8")
            (root / ".cursor-plugin").mkdir()
            (root / ".cursor-plugin" / "plugin.json").write_text(
                json.dumps({"name": "demo", "skills": "./skills", "agents": []}),
                encoding="utf-8",
            )
            overrides = {"skills": ["./custom-skills"]}
            with prepared_plugin_for_install(root, overrides) as prepared:
                self.assertNotEqual(prepared, root.resolve())
                manifest = load_effective_manifest(prepared, None)
                self.assertEqual(manifest["skills"], "./custom-skills")
                validate_override_paths(prepared, overrides)


class TestExternalRepoPathOverrides(unittest.TestCase):
    def test_resolve_skill_from_override_dir(self) -> None:
        alt = FIXTURE_ROOT / "alt-skills"
        self.assertTrue((alt / "commit" / "SKILL.md").is_file())
        sel = resolve_external_specific_selection(
            FIXTURE_ROOT,
            "skill",
            "commit",
            source_path_overrides={"skills": ["./alt-skills"]},
        )
        self.assertEqual(sel.resolved_identifier, "commit")
        self.assertIn("alt-skills", str(sel.source_path))

    def test_materialized_specific_plugin_does_not_reapply_overrides(self) -> None:
        overrides = {"skills": ["./alt-skills"]}
        sel = resolve_external_specific_selection(
            FIXTURE_ROOT,
            "skill",
            "commit",
            source_path_overrides=overrides,
        )
        with materialized_specific_plugin(sel) as plugin_root:
            with self.assertRaises(FileNotFoundError):
                with prepared_plugin_for_install(plugin_root, overrides):
                    pass
            with prepared_plugin_for_install(plugin_root, None) as prepared:
                self.assertTrue((prepared / "skills" / "commit" / "SKILL.md").is_file())


class TestSyntheticPluginIdForUninstall(unittest.TestCase):
    def test_external_unscoped_skill(self) -> None:
        plugin_id = synthetic_plugin_id_for_uninstall("skill", "tdd")
        self.assertEqual(plugin_id, "specific-skill-external-tdd")

    def test_scoped_skill_uses_plugin_prefix(self) -> None:
        plugin_id = synthetic_plugin_id_for_uninstall("skill", "my-plugin:plugin-skill")
        self.assertEqual(plugin_id, "specific-skill-my-plugin-plugin-skill")


class TestCliPathFlag(unittest.TestCase):
    def test_install_plugin_accepts_path(self) -> None:
        from agent_foundry.cli.app import build_parser

        parser = build_parser()
        args = parser.parse_args(
            [
                "install-plugin",
                "cursor-cli",
                "git",
                "--path",
                "skills:./custom-skills",
            ]
        )
        self.assertEqual(args.path_overrides, ["skills:./custom-skills"])
