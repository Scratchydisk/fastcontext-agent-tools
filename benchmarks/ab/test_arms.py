import unittest
from arms import build_command, DIRECTIVE

class TestArms(unittest.TestCase):
    def test_without_has_no_mcp(self):
        argv, env = build_command("without", "find X", "opus", "fc.json", "/repo")
        self.assertIn("--model", argv); self.assertIn("opus", argv)
        self.assertIn("--output-format", argv); self.assertIn("stream-json", argv)
        self.assertNotIn("--mcp-config", argv)
        self.assertNotIn("fastcontext", " ".join(argv))

    def test_with_has_mcp_and_directive(self):
        argv, env = build_command("with", "find X", "opus", "fc.json", "/repo")
        self.assertIn("--mcp-config", argv)
        self.assertIn("fc.json", argv)
        joined = " ".join(argv)
        self.assertIn("fastcontext", joined)        # tool allow-listed
        self.assertIn("--append-system-prompt", argv)

    def test_query_is_in_prompt(self):
        argv, _ = build_command("without", "where is auth", "opus", "fc.json", "/repo")
        self.assertTrue(any("where is auth" in a for a in argv))

    def test_both_arms_skip_permissions(self):
        argv_without, _ = build_command("without", "find X", "opus", "fc.json", "/repo")
        argv_with, _ = build_command("with", "find X", "opus", "fc.json", "/repo")
        self.assertIn("--dangerously-skip-permissions", argv_without)
        self.assertIn("--dangerously-skip-permissions", argv_with)

if __name__ == "__main__":
    unittest.main()
