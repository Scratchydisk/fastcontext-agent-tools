# FastContext end-to-end A/B (locate, large repo) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a harness that runs headless Opus on the sasystem repo's 10 locate queries, with and without FastContext, and produces a per-task table of main-model token cost vs success so the user can judge whether FastContext is worth using on large repos.

**Architecture:** A small Python package under `benchmarks/ab/`. Pure, unit-tested functions for command-building, stream-json scoring, and aggregation; a thin orchestrator that shells out to `claude -p --output-format stream-json` per (task × arm × run), scores each, and writes per-run rows + an aggregate trade table. A probe task verifies the headless output shape (the load-bearing assumption) before any scale spend. Reuses ground truth from `benchmarks/maximkeep/cases.py`.

**Tech Stack:** Python 3.12 (repo `.venv/bin/python`), `unittest`, the `claude` CLI in headless mode, Ollama endpoint on gpu-24.

## Global Constraints

- Python: run everything with `/mnt/wdblue/stewart/Projects/fastcontext-agent-tools/.venv/bin/python`.
- Main agent model: `opus` (the `--model` value passed to `claude -p`).
- WITH-arm FastContext endpoint: gpu-24 `http://192.168.0.248:11434/v1` (DHCP — re-confirm IP at run time), model `fc-q8-nothink-64k:latest`, `API_KEY=ollama`, with `FC_TEMPERATURE=0.2`, `FASTCONTEXT_REROOT_PATHS=1`, `FASTCONTEXT_EXPLORE_RETRIES=2`.
- Tasks + ground truth come from `benchmarks/maximkeep/cases.py` (`CASES`, `TARGET_REPO`); never hard-code the private queries elsewhere.
- Cost discipline: no run beyond the 2-run smoke until its projected cost is printed and approved. N stays 1 until the first-10 review.
- Results are private (sasystem corpus): write under `benchmarks/ab/results/`, which is gitignored; only code + README are committable.

---

### Task 1: Probe the headless output shape (build-risk gate)

Verifies the one load-bearing assumption — that `claude -p --output-format stream-json` reliably yields usage/cost, the final result text, and tool-use events — and captures a real fixture for the scorer. **If the fields aren't present, stop and rethink the instrument.**

**Files:**
- Create: `benchmarks/ab/fixtures/` (dir)
- Create: `benchmarks/ab/fixtures/probe_events.jsonl` (captured real output)
- Create: `benchmarks/ab/fixtures/SHAPE.md` (notes on the fields found)

- [ ] **Step 1: Run a trivial headless capture**

```bash
cd /mnt/wdblue/stewart/Projects/fastcontext-agent-tools
mkdir -p benchmarks/ab/fixtures
claude -p "Reply with the word READY and nothing else." \
  --model opus --output-format stream-json --verbose \
  > benchmarks/ab/fixtures/probe_events.jsonl 2>benchmarks/ab/fixtures/probe.err
echo "exit=$?"; wc -l benchmarks/ab/fixtures/probe_events.jsonl
```
Expected: a non-empty JSONL file, exit 0. If the command errors on flags, try `claude --help | grep -E "output-format|verbose|model|mcp-config|allowedTools"` and adjust the flags here and in Task 3 before continuing.

- [ ] **Step 2: Confirm the required fields exist**

```bash
.venv/bin/python - <<'PY'
import json
events=[json.loads(l) for l in open("benchmarks/ab/fixtures/probe_events.jsonl") if l.strip()]
types=[e.get("type") for e in events]
res=[e for e in events if e.get("type")=="result"]
print("event types:", types)
assert res, "no result event — cannot get usage/cost"
r=res[-1]
print("has usage:", "usage" in r, "| has total_cost_usd:", "total_cost_usd" in r,
      "| has result text:", bool(r.get("result")), "| num_turns:", r.get("num_turns"))
assert "usage" in r and "result" in r, "result event missing usage/result"
print("OK: shape usable")
PY
```
Expected: prints `OK: shape usable`. Record the exact key names (e.g. `usage.input_tokens`, `usage.output_tokens`) in `SHAPE.md`, plus how an assistant `tool_use` event looks (run once more with a tool if needed). **If this assert fails, stop — report that headless usage isn't recoverable and the A/B needs a different capture method.**

- [ ] **Step 3: Write SHAPE.md**

Create `benchmarks/ab/fixtures/SHAPE.md` documenting, from the real capture: the `result` event's path to `result` text, `usage.input_tokens` / `usage.output_tokens`, `total_cost_usd`, `num_turns`, and the shape of an `assistant` event's `message.content[]` `tool_use` block (`name` field). The scorer in Task 2 is written against these exact paths.

- [ ] **Step 4: Commit**

```bash
git add benchmarks/ab/fixtures/SHAPE.md
git commit -m "ab: probe headless claude stream-json shape"
```
(Do not commit `probe_events.jsonl`/`probe.err` — add `benchmarks/ab/fixtures/*.jsonl` and `*.err` to `.gitignore` in this step.)

---

### Task 2: Scorer — parse stream-json events into metrics

**Files:**
- Create: `benchmarks/ab/score.py`
- Test: `benchmarks/ab/test_score.py`

**Interfaces:**
- Produces: `score_events(events: list[dict], truth: set[str], truth_dirs: set[str]) -> dict` returning keys `success: bool`, `area: bool`, `used_fastcontext: bool`, `input_tokens: int`, `output_tokens: int`, `cost_usd: float|None`, `num_turns: int|None`, `tool_calls: list[str]`.

- [ ] **Step 1: Write the failing test**

```python
# benchmarks/ab/test_score.py
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

    def test_area_hit_from_reported_path(self):
        ev = {**RESULT, "result": "Look at src/Api/Auth/Other.cs"}
        s = score_events([ev], {"AuthService.cs"}, {"src/Api/Auth"})
        self.assertFalse(s["success"])
        self.assertTrue(s["area"])

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd benchmarks/ab && ../../.venv/bin/python -m unittest test_score -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'score'`.

- [ ] **Step 3: Write minimal implementation**

```python
# benchmarks/ab/score.py
"""Score one headless `claude -p --output-format stream-json` run."""
from __future__ import annotations
import os, re

# crude path tokens like src/a/b/File.cs or a\b\File.ts
_PATH = re.compile(r"[\w./\\-]+\.[A-Za-z0-9]+")


def score_events(events: list[dict], truth: set[str], truth_dirs: set[str]) -> dict:
    final, usage, cost, turns = "", {}, None, None
    tool_calls: list[str] = []
    for ev in events:
        if ev.get("type") == "assistant":
            for block in ev.get("message", {}).get("content", []) or []:
                if block.get("type") == "tool_use":
                    tool_calls.append(block.get("name") or "")
        elif ev.get("type") == "result":
            final = ev.get("result") or final
            usage = ev.get("usage") or usage
            cost = ev.get("total_cost_usd", cost)
            turns = ev.get("num_turns", turns)
    success = any(b in final for b in truth)
    paths = _PATH.findall(final)
    area = any(os.path.dirname(p).replace("\\", "/").endswith(
        d.replace("\\", "/").lstrip("/")) for p in paths for d in truth_dirs if d) \
        or any(os.path.basename(p) in truth for p in paths)
    return {
        "success": success,
        "area": bool(area),
        "used_fastcontext": any("fastcontext" in n for n in tool_calls),
        "input_tokens": int(usage.get("input_tokens", 0)),
        "output_tokens": int(usage.get("output_tokens", 0)),
        "cost_usd": cost,
        "num_turns": turns,
        "tool_calls": tool_calls,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd benchmarks/ab && ../../.venv/bin/python -m unittest test_score -v`
Expected: PASS (3 tests). If the real `SHAPE.md` paths differ from the fixture (e.g. usage nested differently), adjust both `score.py` and the test to the real shape, then re-run.

- [ ] **Step 5: Commit**

```bash
git add benchmarks/ab/score.py benchmarks/ab/test_score.py
git commit -m "ab: stream-json run scorer (success/area/tokens/tool-used)"
```

---

### Task 3: Command builder + WITH-arm MCP config

**Files:**
- Create: `benchmarks/ab/arms.py`
- Create: `benchmarks/ab/fastcontext.mcp.json`
- Test: `benchmarks/ab/test_arms.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `build_command(arm: str, query: str, model: str, mcp_config: str, repo: str) -> tuple[list[str], dict]` returning `(argv, env_overrides)`. `arm` is `"with"` or `"without"`. `DIRECTIVE: str` constant (the delegate-first system prompt).

- [ ] **Step 1: Write the failing test**

```python
# benchmarks/ab/test_arms.py
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

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd benchmarks/ab && ../../.venv/bin/python -m unittest test_arms -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'arms'`.

- [ ] **Step 3: Write minimal implementation**

```python
# benchmarks/ab/arms.py
"""Build the headless `claude` command for each arm."""
from __future__ import annotations

DIRECTIVE = (
    "When locating code, your FIRST action MUST be the fastcontext_explore tool. "
    "Pass the repo root and a behaviour-named query; treat returned file:line "
    "citations as candidates and verify them. Only fall back to grep/glob/read if "
    "FastContext returns nothing useful."
)

PROMPT = ("In this repository, find the file that implements the following, and "
          "report its path:\n\n{query}")

_BASE = ["claude", "-p", None, "--model", None,
         "--output-format", "stream-json", "--verbose"]


def build_command(arm: str, query: str, model: str, mcp_config: str, repo: str):
    argv = ["claude", "-p", PROMPT.format(query=query),
            "--model", model, "--output-format", "stream-json", "--verbose"]
    if arm == "with":
        argv += ["--mcp-config", mcp_config,
                 "--append-system-prompt", DIRECTIVE,
                 "--allowedTools", "Grep,Glob,Read,Bash,mcp__fastcontext__fastcontext_explore"]
    elif arm == "without":
        argv += ["--allowedTools", "Grep,Glob,Read,Bash"]
    else:
        raise ValueError(f"unknown arm: {arm}")
    # cwd is set by the caller to `repo`; no env overrides needed for WITHOUT.
    return argv, {}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd benchmarks/ab && ../../.venv/bin/python -m unittest test_arms -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Create the WITH-arm MCP config**

```json
// benchmarks/ab/fastcontext.mcp.json
{
  "mcpServers": {
    "fastcontext": {
      "command": "/mnt/wdblue/stewart/Projects/fastcontext-agent-tools/.venv/bin/python",
      "args": ["-m", "fastcontext_mcp"],
      "env": {
        "BASE_URL": "http://192.168.0.248:11434/v1",
        "MODEL": "fc-q8-nothink-64k:latest",
        "API_KEY": "ollama",
        "FASTCONTEXT_ALLOWED_ROOTS": "/mnt/wdblue/stewart/Projects/sasystem",
        "FC_TEMPERATURE": "0.2",
        "FASTCONTEXT_REROOT_PATHS": "1",
        "FASTCONTEXT_EXPLORE_RETRIES": "2"
      }
    }
  }
}
```
(Strip the `// comment` line — JSON. Re-confirm the gpu-24 IP at run time.)

- [ ] **Step 6: Commit**

```bash
git add benchmarks/ab/arms.py benchmarks/ab/test_arms.py benchmarks/ab/fastcontext.mcp.json
git commit -m "ab: per-arm command builder + WITH-arm MCP config"
```

---

### Task 4: Aggregator — rows into a per-task trade table

**Files:**
- Create: `benchmarks/ab/aggregate.py`
- Test: `benchmarks/ab/test_aggregate.py`

**Interfaces:**
- Consumes: run rows shaped like `score_events` output plus `{"task": int, "arm": str}`.
- Produces: `trade_table(rows: list[dict]) -> str` (markdown), and `medians(rows, arm, task) -> dict`.

- [ ] **Step 1: Write the failing test**

```python
# benchmarks/ab/test_aggregate.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd benchmarks/ab && ../../.venv/bin/python -m unittest test_aggregate -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'aggregate'`.

- [ ] **Step 3: Write minimal implementation**

```python
# benchmarks/ab/aggregate.py
"""Aggregate per-run rows into a per-task WITH-vs-WITHOUT trade table."""
from __future__ import annotations
import statistics


def _median(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 3) if xs else None


def medians(rows, arm, task):
    sel = [r for r in rows if r["arm"] == arm and r["task"] == task]
    if not sel:
        return None
    n = len(sel)
    return {
        "n": n,
        "success_pct": round(100 * sum(bool(r["success"]) for r in sel) / n),
        "med_total_tokens": _median([r["input_tokens"] + r["output_tokens"] for r in sel]),
        "med_cost": _median([r.get("cost_usd") for r in sel]),
        "tool_unused": sum(1 for r in sel if arm == "with" and not r.get("used_fastcontext")),
    }


def trade_table(rows) -> str:
    tasks = sorted({r["task"] for r in rows})
    out = ["| task | arm | n | success % | median tokens | median $ | notes |",
           "|---|---|---|---|---|---|---|"]
    for t in tasks:
        for arm in ("without", "with"):
            m = medians(rows, arm, t)
            if not m:
                continue
            note = f"tool not used in {m['tool_unused']}/{m['n']}" if m["tool_unused"] else ""
            out.append(f"| task {t} | {arm} | {m['n']} | {m['success_pct']}% | "
                       f"{m['med_total_tokens']} | {m['med_cost']} | {note} |")
    return "\n".join(out)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd benchmarks/ab && ../../.venv/bin/python -m unittest test_aggregate -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add benchmarks/ab/aggregate.py benchmarks/ab/test_aggregate.py
git commit -m "ab: per-task trade-table aggregator"
```

---

### Task 5: Orchestrator + runbook (integration, cost-gated)

Wires the pieces, runs `claude` per (task × arm × run), and writes rows + the trade table. Verified by the 2-run smoke; **does not** auto-run the full set.

**Files:**
- Create: `benchmarks/ab/run_ab.py`
- Create: `benchmarks/ab/README.md`
- Modify: `.gitignore` (add `benchmarks/ab/results/` and `benchmarks/ab/fixtures/*.jsonl`)

**Interfaces:**
- Consumes: `score_events` (Task 2), `build_command`/`fastcontext.mcp.json` (Task 3), `trade_table` (Task 4), `CASES`/`TARGET_REPO` from `benchmarks/maximkeep/cases.py`.

- [ ] **Step 1: Write the orchestrator**

```python
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
```

- [ ] **Step 2: Add results/fixtures to .gitignore**

Append to `.gitignore`:
```
benchmarks/ab/results/
benchmarks/ab/fixtures/*.jsonl
benchmarks/ab/fixtures/*.err
```

- [ ] **Step 3: Pre-warm the WITH-arm model + confirm endpoint**

```bash
python3 -c "import urllib.request,json;print('models:', [m['id'] for m in json.load(urllib.request.urlopen('http://192.168.0.248:11434/v1/models',timeout=6))['data'] if 'q8-nothink-64k' in m['id']])"
python3 -c "import json,urllib.request;urllib.request.urlopen(urllib.request.Request('http://192.168.0.248:11434/api/generate',data=json.dumps({'model':'fc-q8-nothink-64k:latest','prompt':'ok','keep_alive':'2h','stream':False}).encode(),headers={'Content-Type':'application/json'}),timeout=400).read();print('warmed')"
```
Expected: the model id prints and `warmed`. If gpu-24's IP changed, update `fastcontext.mcp.json` and these commands.

- [ ] **Step 4: Run the smoke test (2 runs) and verify the instrument**

```bash
cd /mnt/wdblue/stewart/Projects/fastcontext-agent-tools
.venv/bin/python benchmarks/ab/run_ab.py --phase smoke
```
Expected: two runs print non-zero `tok=` and a `$` cost, the WITH run shows `fc=True`, and `results/ab-smoke/summary.md` has a trade row for both arms. **Verification gate:** if `tok=0`/`$None` (usage not captured) or the WITH run shows `fc=False` (tool ignored), STOP and fix before spending more — report which.

- [ ] **Step 5: Write README (runbook) and commit code**

Create `benchmarks/ab/README.md` documenting: purpose (links the spec), the three phases and their commands, the cost gate (review `summary.md`'s projected cost before `--phase full`), the WITH-arm endpoint/model, and that `results/` is private/gitignored. Then:
```bash
git add benchmarks/ab/run_ab.py benchmarks/ab/README.md .gitignore
git commit -m "ab: orchestrator + runbook (smoke/batch/full, cost-gated)"
```

- [ ] **Step 6: STOP — hand back for the cost review**

Do **not** run `--phase batch` or `--phase full` automatically. Report the smoke result and projected cost to the user. The first-10 batch (`--phase batch`) and the full run (`--phase full --n N`) are run only on explicit go, with N chosen at the first-10 review (per the spec).

---

## Self-review

**Spec coverage:** arms (T3), 10 cases + ground truth (T5 via cases.py), main-model token + success + area + tool-used metrics (T2), N gating (T5 phases), per-task trade table (T4), controls/pre-warm (T5 step 3), build-risk probe (T1), cost staging + stop (T5 step 4/6), private results gitignored (T5 step 2). Covered.

**Placeholder scan:** no TBD/TODO; every code step has complete code; the MCP-config comment line is flagged for stripping.

**Type consistency:** `score_events` returns the keys consumed by `aggregate.trade_table`/`medians` (`success`, `input_tokens`, `output_tokens`, `cost_usd`, `used_fastcontext`) and the orchestrator adds `task`/`arm`/`run`; `build_command` signature matches its call in `one_run`. Consistent.

**Known soft spot:** exact `claude` CLI flag names and the stream-json field paths are assumed; Task 1 verifies them against reality and Task 1/Task 2 say to adjust if they differ. This is deliberately front-loaded as the build-risk gate.
