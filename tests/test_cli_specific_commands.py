from __future__ import annotations

import unittest

from agent_foundry.cli.app import build_parser


class TestCliSpecificCommands(unittest.TestCase):
    def test_install_specific_parser(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "install-specific",
                "skill",
                "cursor-cli",
                "git:commit",
                "--in-project",
            ]
        )
        self.assertEqual(args.command, "install-specific")
        self.assertEqual(args.kind, "skill")
        self.assertEqual(args.provider, "cursor-cli")
        self.assertEqual(args.identifier, "git:commit")
        self.assertEqual(args.scope, "in_project")

    def test_uninstall_specific_parser(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["uninstall-specific", "agent", "cursor", "senior-ai-engineer"]
        )
        self.assertEqual(args.command, "uninstall-specific")
        self.assertEqual(args.scope, "global")


if __name__ == "__main__":
    unittest.main()
