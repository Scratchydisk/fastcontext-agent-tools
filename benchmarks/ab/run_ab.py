# benchmarks/ab/run_ab.py
"""Run the locate A/B: claude WITH vs WITHOUT FastContext over the maximkeep cases.

Phases (cost-gated):  --phase smoke (1 task x 2 arms) | batch (--tasks 5 x 2 arms, N=1)
                      | full (all tasks x 2 arms x --n N).  Never auto-escalates.
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(BENCH, "maximkeep"))
from arms import build_command  # noqa: E402
from score import score_events  # noqa: E402
from aggregate import trade_table  # noqa: E402
from cases import CASES, TARGET_REPO  # noqa: E402

MCP = os.path.join(HERE, "fastcontext.mcp.json")
RESULTS = os.path.join(HERE, "results")


def truth_dirs(truth):
    dirs = set()
    skip = {"node_modules", ".git", "obj", "bin", "dist", ".venv", ".worktrees"}
    for root, subs, files in os.walk(TARGET_REPO):
        subs[:] = [d for d in subs if d not in skip]
        if any(b in files for b in truth):
            dirs.add(os.path.realpath(root))
    return dirs


def one_run(arm, query, model, timeout):
    argv, env = build_command(arm, query, model, MCP, TARGET_REPO)
    proc = subprocess.run(argv, cwd=TARGET_REPO, capture_output=True, text=True,
                          timeout=timeout, env={**os.environ, **env})
    events = [json.loads(l) for l in proc.stdout.splitlines() if l.strip().startswith("{")]
    return events


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["smoke", "batch", "full"], required=True)
    ap.add_argument("--n", type=int, default=1)
    ap.add_argument("--tasks", type=int, default=5)
    ap.add_argument("--model", default="opus")
    ap.add_argument("--timeout", type=int, default=900)
    a = ap.parse_args()

    cases = list(enumerate(CASES, 1))
    if a.phase == "smoke":
        cases, n = cases[:1], 1
    elif a.phase == "batch":
        cases, n = cases[:a.tasks], 1
    else:
        n = a.n
    tdirs = {i: truth_dirs(truth) for i, (_q, truth, _t) in cases}

    rows, label = [], f"ab-{a.phase}"
    os.makedirs(os.path.join(RESULTS, label), exist_ok=True)
    for i, (query, truth, _t) in cases:
        for arm in ("without", "with"):
            for run in range(n):
                t0 = time.time()
                try:
                    events = one_run(arm, query, a.model, a.timeout)
                    s = score_events(events, truth, tdirs[i])
                except Exception as exc:  # noqa: BLE001
                    print(f"  t{i} {arm} run{run}: FAILED {exc}")
                    s = {"success": False, "area": False, "used_fastcontext": False,
                         "input_tokens": 0, "output_tokens": 0, "cost_usd": None,
                         "num_turns": None, "tool_calls": []}
                s.update(task=i, arm=arm, run=run, wall_s=round(time.time() - t0, 1))
                rows.append(s)
                print(f"  t{i} {arm} run{run}: hit={s['success']} "
                      f"tok={s['input_tokens']+s['output_tokens']} ${s['cost_usd']} "
                      f"fc={s['used_fastcontext']}")

    with open(os.path.join(RESULTS, label, "rows.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    table = trade_table(rows)
    spent = sum(r["cost_usd"] or 0 for r in rows)
    full_runs = len(CASES) * 2 * max(1, a.n)
    projected = spent / max(1, len(rows)) * full_runs
    summary = (f"# A/B {a.phase}\n\nRuns: {len(rows)}  Spent: ${spent:.2f}  "
               f"Projected full ({full_runs} runs): ${projected:.2f}\n\n{table}\n")
    open(os.path.join(RESULTS, label, "summary.md"), "w").write(summary)
    print("\n" + summary)


if __name__ == "__main__":
    main()
