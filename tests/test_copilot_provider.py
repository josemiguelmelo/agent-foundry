from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_foundry.installers.copilot_provider import install_copilot


class TestCopilotProvider(unittest.TestCase):
    def test_install_in_project_mirrors_kinds_into_project_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cwd = Path(tmpdir)
            plugin_root = cwd / "source-plugin"
            (plugin_root / "skills" / "ship-it").mkdir(parents=True)
            (plugin_root / "skills" / "ship-it" / "SKILL.md").write_text(
                "# skill\n", encoding="utf-8"
            )
            (plugin_root / "agents").mkdir(parents=True)
            (plugin_root / "agents" / "reviewer.md").write_text(
                "# reviewer\n", encoding="utf-8"
            )
            (plugin_root / "commands").mkdir(parents=True)
            (plugin_root / "commands" / "implement.md").write_text(
                "# implement\n", encoding="utf-8"
            )
            (plugin_root / "plugin.json").write_text(
                json.dumps(
                    {
                        "name": "demo",
                        "skills": "./skills",
                        "agents": "./agents",
                        "commands": "./commands",
                    }
                ),
                encoding="utf-8",
            )

            with patch("pathlib.Path.cwd", return_value=cwd), patch(
                "agent_foundry.installers.copilot_provider.run_command"
            ) as run:
                install_copilot("demo", plugin_root, in_project=True)

            self.assertFalse(run.called)
            self.assertTrue((cwd / ".github" / "skills" / "ship-it" / "SKILL.md").is_file())
            self.assertTrue((cwd / ".github" / "agents" / "reviewer.md").is_file())
            self.assertTrue((cwd / ".claude" / "commands" / "implement.md").is_file())


if __name__ == "__main__":
    unittest.main()
