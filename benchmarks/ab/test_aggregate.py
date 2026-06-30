import unittest
from aggregate import trade_table

ROWS = [
    {"task": 1, "arm": "without", "success": True,  "input_tokens": 90000, "output_tokens": 500, "cost_usd": 1.4, "used_fastcontext": False},
    {"task": 1, "arm": "with",    "success": True,  "input_tokens": 30000, "output_tokens": 400, "cost_usd": 0.5, "used_fastcontext": True},
    {"task": 1, "arm": "with",    "success": False, "input_tokens": 95000, "output_tokens": 600, "cost_usd": 1.5, "used_fastcontext": True},
]

class TestAggregate(unittest.TestCase):
    def test_table_has_both_arms_and_task(self):
        md = trade_table(ROWS)
        self.assertIn("task 1", md.lower())
        self.assertIn("with", md.lower())
        self.assertIn("without", md.lower())

    def test_flags_unused_tool(self):
        rows = [{"task": 2, "arm": "with", "success": True, "input_tokens": 1, "output_tokens": 1, "cost_usd": 0.1, "used_fastcontext": False}]
        md = trade_table(rows)
        self.assertIn("tool not used", md.lower())

if __name__ == "__main__":
    unittest.main()
