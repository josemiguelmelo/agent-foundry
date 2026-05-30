from __future__ import annotations

import argparse
import json
import os
import unittest
from pathlib import Path
from unittest import mock

from agent_foundry.cli.app import build_parser
from agent_foundry.cli.handlers.provider_common import _install_repo_context
from agent_foundry.installers.specific import (
    materialized_specific_plugin,
    resolve_specific_selection,
)
from agent_foundry.registry.core import resolve_plugin_dir
from agent_foundry.registry.external import (
    LAYOUT_ENV,
    LAYOUT_EXTERNAL,
    is_external_repo,
    is_git_remote_url,
    is_registry_repo,
    prepared_external_plugin_root,
    resolve_external_plugin_dir,
    resolve_external_specific_selection,
)

FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "external-repo"


class TestGitUrlDetection(unittest.TestCase):
    def test_https_url(self) -> None:
        self.assertTrue(is_git_remote_url("https://github.com/org/repo.git"))

    def test_ssh_url(self) -> None:
        self.assertTrue(is_git_remote_url("git@github.com:org/repo.git"))

    def test_local_path_takes_precedence(self) -> None:
        self.assertFalse(is_git_remote_url(str(FIXTURE_ROOT)))


class TestExternalRepoLayout(unittest.TestCase):
    def test_fixture_is_external_not_registry(self) -> None:
        self.assertTrue(is_external_repo(FIXTURE_ROOT))
        self.assertFalse(is_registry_repo(FIXTURE_ROOT))

    def test_resolve_root_skill(self) -> None:
        sel = resolve_external_specific_selection(FIXTURE_ROOT, "skill", "commit")
        self.assertEqual(sel.kind, "skill")
        self.assertEqual(sel.source_plugin_id, "external")
        self.assertTrue((sel.source_path / "SKILL.md").is_file())

    def test_resolve_root_agent(self) -> None:
        sel = resolve_external_specific_selection(FIXTURE_ROOT, "agent", "senior-reviewer")
        self.assertEqual(sel.resolved_identifier, "senior-reviewer")
        self.assertEqual(sel.source_path.name, "senior-reviewer.md")

    def test_resolve_scoped_skill(self) -> None:
        sel = resolve_external_specific_selection(
            FIXTURE_ROOT, "skill", "my-plugin:plugin-skill"
        )
        self.assertEqual(sel.source_plugin_id, "my-plugin")
        self.assertEqual(sel.resolved_identifier, "plugin-skill")

    def test_resolve_scoped_agent(self) -> None:
        sel = resolve_external_specific_selection(
            FIXTURE_ROOT, "agent", "my-plugin:plugin-agent"
        )
        self.assertEqual(sel.source_plugin_id, "my-plugin")
        self.assertEqual(sel.resolved_identifier, "plugin-agent")

    def test_resolve_plugin_dir(self) -> None:
        path = resolve_external_plugin_dir(FIXTURE_ROOT, "my-plugin")
        self.assertTrue((path / "skills" / "plugin-skill" / "SKILL.md").is_file())

    def test_ambiguous_skill_lists_candidates(self) -> None:
        with self.assertRaises(RuntimeError) as ctx:
            resolve_external_specific_selection(FIXTURE_ROOT, "skill", "shared-skill")
        message = str(ctx.exception)
        self.assertIn("ambiguous", message.lower())
        self.assertIn("external:shared-skill", message)
        self.assertIn("other-plugin:shared-skill", message)

    def test_prepared_plugin_without_manifest(self) -> None:
        plugin_root = FIXTURE_ROOT / "plugins" / "my-plugin"
        with prepared_external_plugin_root(plugin_root) as root:
            self.assertTrue((root / "plugin.json").is_file())
            manifest = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["skills"], "./skills")


class TestExternalRepoIntegration(unittest.TestCase):
    def _external_env(self):
        return mock.patch.dict(
            os.environ,
            {
                "AGENT_FOUNDRY_REPO": str(FIXTURE_ROOT),
                LAYOUT_ENV: LAYOUT_EXTERNAL,
            },
            clear=False,
        )

    def test_resolve_specific_selection_under_external_layout(self) -> None:
        with self._external_env():
            sel = resolve_specific_selection("skill", "commit")
        self.assertEqual(sel.source_plugin_id, "external")

    def test_resolve_plugin_dir_under_external_layout(self) -> None:
        with self._external_env():
            path = resolve_plugin_dir("my-plugin")
        self.assertEqual(path.name, "my-plugin")

    def test_materialize_external_skill(self) -> None:
        with self._external_env():
            sel = resolve_specific_selection("skill", "commit")
        with materialized_specific_plugin(sel) as root:
            self.assertTrue((root / "skills" / "commit" / "SKILL.md").is_file())


class TestInstallRepoContext(unittest.TestCase):
    def test_local_external_repo_sets_layout_env(self) -> None:
        args = argparse.Namespace(repo=str(FIXTURE_ROOT))
        with _install_repo_context(args):
            self.assertEqual(os.environ.get("AGENT_FOUNDRY_REPO"), str(FIXTURE_ROOT.resolve()))
            self.assertEqual(os.environ.get(LAYOUT_ENV), LAYOUT_EXTERNAL)
        self.assertIsNone(os.environ.get(LAYOUT_ENV))

    @mock.patch("agent_foundry.cli.handlers.provider_common.shallow_clone_repo")
    def test_git_url_clone_sets_external_layout(
        self, shallow_clone: mock.MagicMock
    ) -> None:
        import shutil

        def _fake_clone(url: str, *, dest: Path) -> Path:
            dest.mkdir(parents=True, exist_ok=True)
            shutil.copytree(FIXTURE_ROOT, dest, dirs_exist_ok=True)
            return dest

        shallow_clone.side_effect = _fake_clone
        args = argparse.Namespace(repo="https://github.com/example/ext.git")
        with _install_repo_context(args):
            self.assertEqual(os.environ.get(LAYOUT_ENV), LAYOUT_EXTERNAL)
        shallow_clone.assert_called_once()


class TestUninstallPluginRepoFlag(unittest.TestCase):
    def test_uninstall_plugin_accepts_repo(self) -> None:
        args = build_parser().parse_args(
            [
                "uninstall-plugin",
                "cursor-cli",
                "my-plugin",
                "--repo",
                str(FIXTURE_ROOT),
            ]
        )
        self.assertEqual(args.command, "uninstall-plugin")
        self.assertEqual(args.repo, str(FIXTURE_ROOT))


if __name__ == "__main__":
    unittest.main()
