from __future__ import annotations

import json
import unittest
from pathlib import Path

from agent_foundry.installers.specific import (
    materialized_specific_plugin,
    resolve_specific_selection,
)


class TestSpecificInstallers(unittest.TestCase):
    def test_resolve_skill_selection(self) -> None:
        sel = resolve_specific_selection("skill", "git:commit")
        self.assertEqual(sel.kind, "skill")
        self.assertEqual(sel.source_plugin_id, "git")
        self.assertEqual(sel.resolved_identifier, "commit")
        self.assertTrue((sel.source_path / "SKILL.md").is_file())

    def test_resolve_agent_selection_accepts_stem(self) -> None:
        sel = resolve_specific_selection("agent", "senior-ai-engineer")
        self.assertEqual(sel.kind, "agent")
        self.assertEqual(sel.resolved_identifier, "senior-ai-engineer")
        self.assertEqual(sel.source_path.suffix, ".md")

    def test_materialize_skill_plugin(self) -> None:
        sel = resolve_specific_selection("skill", "git:create-branch")
        with materialized_specific_plugin(sel) as root:
            manifest = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["skills"], "./skills")
            self.assertTrue((root / "skills" / "create-branch" / "SKILL.md").is_file())

    def test_materialize_agent_plugin(self) -> None:
        sel = resolve_specific_selection("agent", "senior-product-manager")
        with materialized_specific_plugin(sel) as root:
            manifest = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["agents"], ["./agents/senior-product-manager.md"])
            self.assertTrue((root / "agents" / "senior-product-manager.md").is_file())

    def test_mcp_requires_existing_server(self) -> None:
        with self.assertRaises(RuntimeError):
            resolve_specific_selection("mcp-config", "missing-server")


if __name__ == "__main__":
    unittest.main()
