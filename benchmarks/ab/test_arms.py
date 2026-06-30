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

    # --- Isolation assertions: lock in the contamination fix ---

    def test_both_arms_have_strict_mcp_config(self):
        """Both arms must carry --strict-mcp-config so sasystem's project .mcp.json
        (and any user-level MCP config) cannot inject rogue servers."""
        for arm in ("without", "with"):
            argv, _ = build_command(arm, "find X", "opus", "fc.json", "/repo")
            self.assertIn("--strict-mcp-config", argv,
                          f"arm '{arm}' is missing --strict-mcp-config")

    def test_both_arms_disallow_toolsearch_skill_task_agent(self):
        """Both arms must disallow ToolSearch, Skill, Task, and Agent.
        ToolSearch: prevents deferred MCP schema loading from the session registry.
        Skill: the environment exposes a /fastcontext skill — a direct backdoor.
        Task/Agent: can spawn subagents with full tool access, bypassing arm isolation."""
        required = {"ToolSearch", "Skill", "Task", "Agent"}
        for arm in ("without", "with"):
            argv, _ = build_command(arm, "find X", "opus", "fc.json", "/repo")
            self.assertIn("--disallowedTools", argv,
                          f"arm '{arm}' is missing --disallowedTools")
            idx = argv.index("--disallowedTools")
            disallowed_set = set(argv[idx + 1].split(","))
            missing = required - disallowed_set
            self.assertFalse(missing,
                             f"arm '{arm}' is missing from --disallowedTools: {missing}")

    def test_without_has_no_mcp_config_path(self):
        """WITHOUT arm must not reference any mcp-config path; combined with
        --strict-mcp-config this guarantees zero MCP servers."""
        argv, _ = build_command("without", "find X", "opus", "fc.json", "/repo")
        self.assertNotIn("--mcp-config", argv)

    def test_with_strict_and_mcp_config(self):
        """WITH arm must carry both --strict-mcp-config and its fastcontext
        mcp-config path so only the intended server is reachable."""
        argv, _ = build_command("with", "find X", "opus", "fc.json", "/repo")
        self.assertIn("--strict-mcp-config", argv)
        self.assertIn("--mcp-config", argv)
        idx = argv.index("--mcp-config")
        self.assertEqual(argv[idx + 1], "fc.json")

if __name__ == "__main__":
    unittest.main()
