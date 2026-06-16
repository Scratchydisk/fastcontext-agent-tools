from __future__ import annotations

from collections.abc import Callable
from typing import Any

BenchmarkRunner = Callable[[dict[str, Any]], dict[str, Any]]


def query_variants(task: dict[str, Any]) -> list[dict[str, Any]]:
    variants = task.get("query_variants")
    if not variants:
        return [{**task, "variant_id": "default"}]
    expanded = []
    for variant in variants:
        expanded.append(
            {
                **task,
                **variant,
                "id": f"{task['id']}:{variant['id']}",
                "variant_id": variant["id"],
                "question": variant["question"],
            }
        )
    return expanded


def summarize_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    deltas = [
        float(run["fastcontext_after_verified"]["delta_vs_direct_percent"])
        for run in runs
    ]
    successful = [
        run
        for run in runs
        if run["fastcontext_after_raw"]["returncode"] == 0
        and run["fastcontext_after_raw"]["found_all_ground_truth_files"]
    ]
    successful_deltas = [
        float(run["fastcontext_after_verified"]["delta_vs_direct_percent"])
        for run in successful
    ]
    return {
        "runs": len(runs),
        "successful_runs": len(successful),
        "best_successful_delta_vs_direct_percent": (
            min(successful_deltas) if successful_deltas else None
        ),
        "best_delta_vs_direct_percent": min(deltas),
        "median_delta_vs_direct_percent": sorted(deltas)[len(deltas) // 2],
        "worst_delta_vs_direct_percent": max(deltas),
    }


def benchmark_task_matrix(
    task: dict[str, Any],
    repeats: int,
    runner: BenchmarkRunner,
) -> dict[str, Any]:
    variants = []
    for variant in query_variants(task):
        runs = []
        for run_index in range(1, repeats + 1):
            run = runner(variant)
            run["run_index"] = run_index
            runs.append(run)
        variants.append(
            {
                "id": variant["variant_id"],
                "question": variant["question"],
                "runs": runs,
                "aggregate": summarize_runs(runs),
            }
        )
    return {
        "id": task["id"],
        "project_under_test": task["repo_path"],
        "repeats": repeats,
        "variants": variants,
    }
