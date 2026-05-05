import unittest


class TestCliSmoke(unittest.TestCase):
    def test_cli_module_imports(self) -> None:
        import agent_foundry.cli as cli

        self.assertTrue(hasattr(cli, "main"))
