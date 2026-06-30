# A/B Harness — FastContext locate benchmark

Measures whether the `fastcontext_explore` tool improves file-locate accuracy
and reduces token cost on the Maxim Keep monorepo (a large private .NET 10 +
Nuxt 3 + Node MCP polyglot repo). Full spec:
[docs/superpowers/specs/2026-06-30-fastcontext-end-to-end-ab.md](../../docs/superpowers/specs/2026-06-30-fastcontext-end-to-end-ab.md)

## Arms

| Arm | Description |
|-----|-------------|
| **WITHOUT** | `claude` with `Grep,Glob,Read,Bash` only — no FastContext |
| **WITH** | `claude` with the above tools + `mcp__fastcontext__fastcontext_explore`, directed by a system-prompt directive to use it first |

WITH-arm FastContext endpoint: `http://192.168.0.248:11434/v1` (gpu-24, RTX 5090 24 GB)  
WITH-arm model: `fc-q8-nothink-64k:latest` (64k context, Q8, no-think)

## Phases

Three cost-gated phases — **never auto-escalates**; each needs explicit go:

| Phase | Cases | Arms | Runs each | Approx cost |
|-------|-------|------|-----------|-------------|
| `smoke` | 1 | 2 | 1 | ~$1.50 |
| `batch` | 5 (default) | 2 | 1 | ~$8 |
| `full` | all 10 | 2 | N (choose at batch review) | ~$15–$60+ |

### Commands

```bash
# Smoke (2 runs — mandatory gate before anything else)
.venv/bin/python benchmarks/ab/run_ab.py --phase smoke

# Batch (first-10 cost review — choose N after reviewing smoke summary)
.venv/bin/python benchmarks/ab/run_ab.py --phase batch --tasks 5

# Full (only after explicit human go-ahead at batch review)
.venv/bin/python benchmarks/ab/run_ab.py --phase full --n 3
```

## Cost gate

**Always review `results/ab-<phase>/summary.md` before escalating to the next
phase.** The summary prints:

```
Runs: N  Spent: $X.XX  Projected full (20 runs): $Y.YY
```

Do not run `--phase full` until you have reviewed the projected cost at batch
and chosen an appropriate `--n`. The default model is `opus`; to use a cheaper
model for exploration add `--model sonnet`.

## Pre-warm

Before running a phase, warm the WITH-arm model (keeps it loaded for 2 h):

```bash
python3 -c "
import json, urllib.request
urllib.request.urlopen(
    urllib.request.Request(
        'http://192.168.0.248:11434/api/generate',
        data=json.dumps({'model': 'fc-q8-nothink-64k:latest',
                         'prompt': 'ok', 'keep_alive': '2h',
                         'stream': False}).encode(),
        headers={'Content-Type': 'application/json'}
    ), timeout=400
).read()
print('warmed')
"
```

## Results

`results/` is gitignored — raw LLM output is private. Results are stored at:

```
benchmarks/ab/results/ab-<phase>/
  rows.jsonl     # one JSON object per run
  summary.md     # trade table + cost summary
```

## Known concern (smoke observation)

During the smoke run, the WITHOUT arm called `mcp__fastcontext__fastcontext_explore`
via `ToolSearch` (deferred tool discovery), even though `--allowedTools` only
listed `Grep,Glob,Read,Bash`. This means fastcontext is leaking into the control
arm through Claude Code's ambient MCP registry — the `--allowedTools` flag does
not block deferred-tool loading.

**Impact:** the WITHOUT arm's `used_fastcontext` flag will be `True`, making the
WITH vs WITHOUT comparison of `fc=` unreliable. The hit/success and token metrics
are still valid. Mitigations to consider before `--phase batch`:

1. Run WITHOUT arm in a clean environment with no FastContext MCP available at all.
2. Use `--disallowedTools mcp__fastcontext__fastcontext_explore` if that flag exists.
3. Exclude `ToolSearch` from both arms via `--allowedTools`.
