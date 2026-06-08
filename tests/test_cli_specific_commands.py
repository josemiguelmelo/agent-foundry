from __future__ import annotations

import unittest
from unittest.mock import patch

from agent_foundry.cli.app import build_parser


class TestCliSpecificCommands(unittest.TestCase):
    def test_install_parser(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "install",
                "skill",
                "cursor-cli",
                "git:commit",
                "--in-project",
            ]
        )
        self.assertEqual(args.command, "install")
        self.assertEqual(args.kind, "skill")
        self.assertEqual(args.provider, "cursor-cli")
        self.assertEqual(args.identifier, "git:commit")
        self.assertEqual(args.scope, "in_project")

    def test_uninstall_parser(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["uninstall", "agent", "cursor", "senior-ai-engineer"]
        )
        self.assertEqual(args.command, "uninstall")
        self.assertEqual(args.scope, "global")

    def test_install_plugin_parser(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["install-plugin", "codex", "git"])
        self.assertEqual(args.command, "install-plugin")
        self.assertEqual(args.provider, "codex")
        self.assertEqual(args.plugin, "git")
        self.assertEqual(args.scope, "global")

    def test_uninstall_plugin_parser(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["uninstall-plugin", "cursor-cli", "git", "--in-project"]
        )
        self.assertEqual(args.command, "uninstall-plugin")
        self.assertEqual(args.provider, "cursor-cli")
        self.assertEqual(args.plugin, "git")
        self.assertEqual(args.scope, "in_project")

    def test_version_flag(self) -> None:
        parser = build_parser()
        with patch(
            "agent_foundry.cli.app.installed_version",
            return_value="1.0.0",
        ):
            with self.assertRaises(SystemExit) as ctx:
                parser.parse_args(["--version"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
