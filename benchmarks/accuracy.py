"""Accuracy benchmark: does FastContext cite the right files?

For each case it runs an exploration and checks whether any returned citation
lands on an accepted ground-truth file. Writes results/accuracy.md.

    python benchmarks/accuracy.py
"""
from __future__ import annotations

import datetime
import json
import os

from _common import config_lines, explore
from cases import CASES, TARGET_REPO


def traj_tool_calls(tp: str | None) -> int:
    if not tp or not os.path.exists(tp):
        return 0
    n = 0
    for line in open(tp):
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("role") == "assistant" and ev.get("tool_calls"):
            n += len(ev["tool_calls"])
    return n


def main() -> None:
    iters = int(os.getenv("BENCH_ITERS", "1"))
    rows, hits, attempts, timeouts = [], 0, 0, 0
    for query, truth, _terms in CASES:
        case_hits, calls_sum, files_seen, case_timeouts = 0, 0, set(), 0
        for _ in range(iters):
            try:
                res = explore(TARGET_REPO, query)
            except Exception as exc:  # noqa: BLE001 — a timeout/error is a miss, keep going
                print(f"  query failed (counted as miss): {exc}")
                res = {}
                case_timeouts += 1
                timeouts += 1
            files = {os.path.basename(c["path"]) for c in (res.get("citations") or [])}
            files_seen |= files
            case_hits += any(f in truth for f in files)
            calls_sum += traj_tool_calls(res.get("trajectory_path"))
            attempts += 1
        hits += case_hits
        files_label = sorted(files_seen) or (["(timeout)"] if case_timeouts == iters else ["(none)"])
        rows.append(
            {
                "hit": f"{case_hits}/{iters}" if iters > 1 else ("YES" if case_hits else "no"),
                "files": files_label,
                "avg_calls": round(calls_sum / iters, 1),
            }
        )

    lines = [
        "# Accuracy benchmark",
        "",
        f"Run: {datetime.date.today().isoformat()}",
        f"Iterations per query: {iters}",
        "",
        *config_lines(),
        "",
        f"**File-hit rate: {hits}/{attempts}**"
        + (f" ({timeouts} attempt(s) timed out, counted as misses)" if timeouts else ""),
        "",
        "| # | hits | files cited (any iter) | avg tool calls |",
        "|---|------|------------------------|----------------|",
    ]
    for i, r in enumerate(rows, 1):
        lines.append(f"| {i} | {r['hit']} | {', '.join(r['files'])} | {r['avg_calls']} |")
    lines += [
        "",
        "A *hit* means a returned citation pointed at an accepted ground-truth "
        "file for that query. A miss returned either no citation or one on a "
        "different file. Results vary run to run (sampling); re-run to confirm.",
        "",
    ]
    report = "\n".join(lines)

    out = os.path.join(os.path.dirname(__file__), "results", os.getenv("BENCH_LABEL", ""), "accuracy.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(report)
    print(report)
    print(f"written: {out}")


if __name__ == "__main__":
    main()
