from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

token_benchmark_matrix = importlib.import_module("evaluation.token_benchmark_matrix")
RunValue = str | int | float | bool | dict[str, int | float | bool]


class TokenBenchmarkTests(unittest.TestCase):
    def test_matrix_mode_runs_each_query_variant_repeatedly(self) -> None:
        task = {
            "id": "sample",
            "repo_path": "/tmp/sample",
            "question": "natural query",
            "query_variants": [
                {"id": "natural", "question": "natural query"},
                {"id": "symbol", "question": "symbol query"},
            ],
        }

        def fake_benchmark(variant: dict[str, str]) -> dict[str, RunValue]:
            return {
                "id": variant["id"],
                "question": variant["question"],
                "fastcontext_after_raw": {
                    "returncode": 0,
                    "found_all_ground_truth_files": variant["question"] == "symbol query",
                },
                "fastcontext_after_verified": {
                    "delta_vs_direct_percent": -25.0
                    if variant["question"] == "symbol query"
                    else 10.0,
                },
            }

        result = token_benchmark_matrix.benchmark_task_matrix(
            task,
            repeats=2,
            runner=fake_benchmark,
        )

        self.assertEqual(result["id"], "sample")
        self.assertEqual(len(result["variants"]), 2)
        natural = result["variants"][0]
        symbol = result["variants"][1]
        self.assertEqual(natural["aggregate"]["runs"], 2)
        self.assertEqual(natural["aggregate"]["successful_runs"], 0)
        self.assertIsNone(natural["aggregate"]["best_successful_delta_vs_direct_percent"])
        self.assertEqual(symbol["aggregate"]["successful_runs"], 2)
        self.assertEqual(symbol["aggregate"]["best_successful_delta_vs_direct_percent"], -25.0)
        self.assertEqual(symbol["aggregate"]["best_delta_vs_direct_percent"], -25.0)
        self.assertEqual(symbol["runs"][1]["run_index"], 2)


if __name__ == "__main__":
    unittest.main()
