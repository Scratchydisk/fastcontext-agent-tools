# Large-repo benchmark — Maxim Keep

Tests whether a larger `num_ctx` (and/or more `max_turns`) improves FastContext
accuracy on a **large** codebase — the question the upstream `benchmarks/` set
can't answer because its target repo fits inside 16k.

> **Private corpus.** Maxim Keep (a large .NET 10 + Nuxt 3 + Node MCP monorepo —
> ~2,000 tracked files, ~433k LOC: C# 222k, Vue/TS 165k, JS 34k, SQL 12k; vs the
> upstream bench target's ~1.4k LOC) is a **private repository, not available to
> other users** and not bundled
> here. These cases/results are committed for methodology and for the
> maintainers' own measurements — external users can't reproduce the file-hit
> numbers without access to that corpus. The default `FASTCONTEXT_BENCH_REPO`
> path is machine-specific; point it at your own large repo (with your own
> verified `cases.py`) to run an equivalent test.

- **Cases:** [`cases.py`](cases.py) — 10 "where is X" queries spanning the Maxim
  Keep C# backend / Vue+TS frontend / JS MCP, each with a hand-verified
  ground-truth file (the definition/implementation, not callers).
- **Runner:** [`accuracy.py`](accuracy.py) — same metric as the upstream
  accuracy benchmark (file-hit rate), reusing `../_common.py` unchanged; adds
  `BENCH_MAXTURNS`.
- **Results:** written to `results/<BENCH_LABEL>/accuracy.md`.

## Why two knobs

| Knob | How to vary | Hypothesis |
|---|---|---|
| `num_ctx` | point `MODEL` at a different Ollama alias (16k vs 32k vs 64k) — it's set in the model's Modelfile, not a request flag | a large repo's exploration trajectory exceeds 16k, so a bigger window may avoid truncating earlier steps |
| `max_turns` | `BENCH_MAXTURNS` (default 10; upstream MCP default is 6) | a large repo may need more grep/glob/read steps to traverse; coverage may be turn-bound, not context-bound |

Run both so we can tell which (if either) is the real large-codebase lever —
rather than assuming. (Upstream EXPERIMENTS.md exp 8 found no accuracy gain from
64k **on a small repo**; this set is the missing large-repo measurement.)

## Prerequisites

- Run with the repo venv that has FastContext installed:
  `/mnt/wdblue/stewart/Projects/fastcontext-agent-tools/.venv/bin/python`.
- A reachable Ollama endpoint with the model alias(es) at the desired `num_ctx`.
  On pve-3: `fc-q4-nothink-16k:latest` (existing) and `fc-q4-nothink-32k:latest`
  (being built). To add 64k: `ollama show fc-q4-nothink-16k:latest --modelfile`,
  change `PARAMETER num_ctx 16384` → `65536`, `ollama create fc-q4-nothink-64k -f -`.
- `BENCH_TIMEOUT` (default 220s) may need raising for big-context runs.

## Running the matrix

From the repo root. `API_KEY` is ignored by Ollama (any non-empty value):

```bash
VENV=/mnt/wdblue/stewart/Projects/fastcontext-agent-tools/.venv/bin/python
export BASE_URL=http://192.168.0.4:11434/v1 API_KEY=ollama
export FASTCONTEXT_BENCH_REPO=/mnt/wdblue/stewart/Projects/sasystem
export BENCH_ITERS=3            # 3 attempts/query to average out sampling noise

# 16k x max_turns 6 and 12
BENCH_LABEL=mk-16k-t6  BENCH_NUM_CTX=16384 BENCH_MAXTURNS=6  MODEL=fc-q4-nothink-16k:latest $VENV benchmarks/maximkeep/accuracy.py
BENCH_LABEL=mk-16k-t12 BENCH_NUM_CTX=16384 BENCH_MAXTURNS=12 MODEL=fc-q4-nothink-16k:latest $VENV benchmarks/maximkeep/accuracy.py

# 32k x max_turns 6 and 12  (once the 32k alias exists)
BENCH_LABEL=mk-32k-t6  BENCH_NUM_CTX=32768 BENCH_MAXTURNS=6  MODEL=fc-q4-nothink-32k:latest $VENV benchmarks/maximkeep/accuracy.py
BENCH_LABEL=mk-32k-t12 BENCH_NUM_CTX=32768 BENCH_MAXTURNS=12 MODEL=fc-q4-nothink-32k:latest $VENV benchmarks/maximkeep/accuracy.py
```

Then compare the `File-hit rate` lines across `results/mk-*/accuracy.md`.

## Reading the result

- If 32k > 16k at the same `max_turns` → context **is** a large-repo lever
  (confirms the hypothesis the upstream small-repo bench couldn't test).
- If t12 > t6 at the same `num_ctx` → coverage was **turn**-bound, not
  context-bound (raise the MCP `max_turns` default for large repos instead).
- If neither moves beyond sampling noise → the 4B model's agentic competence is
  the ceiling on this repo, and neither knob is worth changing (matches the
  upstream "limiter is the small model" finding).

Treat absolute numbers as indicative — 10 queries is small and sampling-noisy.
