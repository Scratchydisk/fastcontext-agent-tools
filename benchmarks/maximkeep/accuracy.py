"""Large-repo accuracy benchmark (Maxim Keep).

Mirrors ../accuracy.py but runs the large-repo cases in ./cases.py and lets you
vary max_turns (BENCH_MAXTURNS) so a num_ctx x max_turns matrix can be swept.
Reuses the shared endpoint setup + explore() from ../_common.py unchanged.

num_ctx is endpoint-side (set by the Ollama model's Modelfile), so it is NOT a
flag here: point MODEL at the alias built at the desired context (e.g.
fc-q4-nothink-16k vs fc-q4-nothink-32k) and record it via BENCH_NUM_CTX +
BENCH_LABEL. Everything else (temp, reroot, retry-on-empty) stays at the
adopted defaults from _common.

    # one cell of the matrix:
    BENCH_LABEL=maximkeep-16k-t6 BENCH_NUM_CTX=16384 BENCH_MAXTURNS=6 \
    MODEL=fc-q4-nothink-16k:latest BASE_URL=http://192.168.0.4:11434/v1 API_KEY=ollama \
    .venv/bin/python benchmarks/maximkeep/accuracy.py
"""
from __future__ import annotations

import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
sys.path.insert(0, BENCH)   # ../_common.py
sys.path.insert(0, HERE)    # ./cases.py

from _common import config_lines, explore  # noqa: E402
from cases import CASES, TARGET_REPO  # noqa: E402


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
    max_turns = int(os.getenv("BENCH_MAXTURNS", "10"))
    num_ctx = os.getenv("BENCH_NUM_CTX", "(unset — set to the alias's Modelfile num_ctx)")
    rows, hits, attempts, timeouts = [], 0, 0, 0

    for query, truth, _terms in CASES:
        case_hits, calls_sum, files_seen, case_timeouts = 0, 0, set(), 0
        for _ in range(iters):
            try:
                res = explore(TARGET_REPO, query, max_turns=max_turns)
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
                "truth": sorted(truth),
                "files": files_label,
                "avg_calls": round(calls_sum / iters, 1),
            }
        )

    lines = [
        "# Accuracy benchmark — Maxim Keep (large repo)",
        "",
        f"Run: {datetime.date.today().isoformat()}",
        f"Target repo: `{TARGET_REPO}`",
        f"Iterations per query: {iters}",
        f"max_turns: {max_turns}",
        f"num_ctx: `{num_ctx}`",
        "",
        *config_lines(),
        "",
        f"**File-hit rate: {hits}/{attempts}**"
        + (f" ({timeouts} attempt(s) timed out, counted as misses)" if timeouts else ""),
        "",
        "| # | hits | expected | files cited (any iter) | avg tool calls |",
        "|---|------|----------|------------------------|----------------|",
    ]
    for i, r in enumerate(rows, 1):
        lines.append(
            f"| {i} | {r['hit']} | {', '.join(r['truth'])} | {', '.join(r['files'])} | {r['avg_calls']} |"
        )
    lines += [
        "",
        "A *hit* means a returned citation pointed at the accepted ground-truth "
        "file (the file that defines/implements the behaviour). Results vary run "
        "to run (sampling); use BENCH_ITERS>1 and re-run to confirm.",
        "",
    ]
    report = "\n".join(lines)

    out = os.path.join(HERE, "results", os.getenv("BENCH_LABEL", "unlabelled"), "accuracy.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(report)
    print(report)
    print(f"written: {out}")


if __name__ == "__main__":
    main()
