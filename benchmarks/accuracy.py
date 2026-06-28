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
    rows, hits = [], 0
    for query, truth, _terms in CASES:
        res = explore(TARGET_REPO, query)
        files = sorted({os.path.basename(c["path"]) for c in (res.get("citations") or [])})
        hit = any(f in truth for f in files)
        hits += hit
        rows.append(
            {
                "query": query,
                "hit": hit,
                "files": files or ["(none)"],
                "warnings": len(res.get("citation_warnings") or []),
                "tool_calls": traj_tool_calls(res.get("trajectory_path")),
            }
        )

    lines = [
        "# Accuracy benchmark",
        "",
        f"Run: {datetime.date.today().isoformat()}",
        "",
        *config_lines(),
        "",
        f"**File-hit rate: {hits}/{len(CASES)}**",
        "",
        "| # | hit | files cited | warnings | tool calls |",
        "|---|-----|-------------|----------|------------|",
    ]
    for i, r in enumerate(rows, 1):
        lines.append(
            f"| {i} | {'YES' if r['hit'] else 'no'} | {', '.join(r['files'])} "
            f"| {r['warnings']} | {r['tool_calls']} |"
        )
    lines += [
        "",
        "A *hit* means a returned citation pointed at an accepted ground-truth "
        "file for that query. A miss returned either no citation or one on a "
        "different file. Results vary run to run (sampling); re-run to confirm.",
        "",
    ]
    report = "\n".join(lines)

    out = os.path.join(os.path.dirname(__file__), "results", "accuracy.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(report)
    print(report)
    print(f"written: {out}")


if __name__ == "__main__":
    main()
