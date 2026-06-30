import unittest
from score import score_events

RESULT = {
    "type": "result", "result": "The file is src/Api/Auth/AuthService.cs which issues the JWT.",
    "usage": {"input_tokens": 1200, "output_tokens": 80}, "total_cost_usd": 0.05, "num_turns": 4,
}
ASSIST_FC = {"type": "assistant", "message": {"content": [
    {"type": "tool_use", "name": "mcp__fastcontext__fastcontext_explore", "input": {}}]}}
ASSIST_GREP = {"type": "assistant", "message": {"content": [
    {"type": "tool_use", "name": "Grep", "input": {}}]}}

class TestScore(unittest.TestCase):
    def test_success_and_tokens(self):
        s = score_events([ASSIST_GREP, RESULT], {"AuthService.cs"}, {"/repo/src/Api/Auth"})
        self.assertTrue(s["success"])
        self.assertEqual(s["input_tokens"], 1200)
        self.assertEqual(s["output_tokens"], 80)
        self.assertEqual(s["cost_usd"], 0.05)
        self.assertFalse(s["used_fastcontext"])

    def test_miss_and_fastcontext_flag(self):
        s = score_events([ASSIST_FC, {**RESULT, "result": "It is in Program.cs"}],
                         {"AuthService.cs"}, {"/repo/src/Api/Auth"})
        self.assertFalse(s["success"])
        self.assertTrue(s["used_fastcontext"])
        self.assertFalse(s["area"])

    def test_area_hit_from_reported_path(self):
        # truth_dir is ABSOLUTE (as run_ab produces); reported path is repo-relative
        ev = {**RESULT, "result": "Look at src/Api/Auth/Other.cs"}
        s = score_events([ev], {"AuthService.cs"},
                         {"/mnt/wdblue/stewart/Projects/sasystem/src/Api/Auth"})
        self.assertFalse(s["success"])
        self.assertTrue(s["area"])

    def test_area_miss_unrelated_dir(self):
        # absolute truth_dir, reported path in a completely different dir — must NOT hit
        ev = {**RESULT, "result": "Look at src/Other/Module/Foo.cs"}
        s = score_events([ev], {"AuthService.cs"},
                         {"/mnt/wdblue/stewart/Projects/sasystem/src/Api/Auth"})
        self.assertFalse(s["success"])
        self.assertFalse(s["area"])

    def test_area_miss_bare_filename(self):
        # bare filename (no dirname) must NOT trigger an area hit
        ev = {**RESULT, "result": "Look at AuthService.cs for details"}
        s = score_events([ev], {"Other.cs"},
                         {"/mnt/wdblue/stewart/Projects/sasystem/src/Api/Auth"})
        self.assertFalse(s["area"])

if __name__ == "__main__":
    unittest.main()
