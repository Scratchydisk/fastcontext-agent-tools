# Benchmarks

Three layers, from "is the locator accurate?" up to "does using it actually make
a coding agent better?":

1. **Isolated locator** (`accuracy.py`, `token_usage.py`) — does the explorer cite
   the right files, and how much context does it save? Small repo (this one).
2. **Large-repo locator** (`maximkeep/`) — the same, on a ~433k-LOC private
   codebase. See [maximkeep/results/FINDINGS.md](maximkeep/results/FINDINGS.md).
3. **End-to-end A/B** (`ab/`) — the one that matters: does a *main agent* (Claude
   or a local model) solve locate tasks better/cheaper WITH FastContext than
   without? See [ab/RESULTS.md](ab/RESULTS.md).

## Does it actually help? (the honest headline)

The end-to-end A/B ran the same locate tasks WITH vs WITHOUT FastContext, across a
strong and a weak main agent, on an easy and a hard repo (file-hit, WITHOUT → WITH):

| | small repo (easy) | large repo (hard) |
|---|---|---|
| **Opus** (strong main agent) | 100 → 100 | 94 → 94 |
| **Qwen3.6-35B** (weak, local) | 100 → 100 | **60 → 66** |

**FastContext earns its keep in exactly one cell: a weak/local main agent on a
large, hard repo** — and even there the lift is modest (~+6 pts) and costs latency.
A strong agent doesn't need it (either repo); an easy repo leaves no room (either
agent). The value tracks the *main agent's* need, not the locator's standalone
accuracy — which is why the isolated-locator numbers below (great on small, ~40–50%
on large) are necessary but not sufficient to answer "is it worth it."

## The isolated-locator benchmarks

`accuracy.py` and `token_usage.py` run a fixed set of "where is X" questions
(`cases.py`) whose answers are known in this repository's own source, so this repo
is the corpus.

## Running

You need a FastContext endpoint reachable from this machine (see the project
[README](../README.md) and [docs/running-locally.md](../docs/running-locally.md)).
Point the scripts at it and run from the repo root:

```bash
export BASE_URL="http://127.0.0.1:30000/v1"   # your endpoint (or an SSH tunnel)
export API_KEY=""                              # match the server's --api-key
python benchmarks/accuracy.py
python benchmarks/token_usage.py
```

Defaults are filled in for anything unset (`FASTCONTEXT_REROOT_PATHS=1`,
`FC_MAX_TOKENS=4000`, `FASTCONTEXT_ALLOWED_ROOTS=/`, model
`FastContext-1.0-4B-RL`). Each script writes a dated report under `results/` and
prints it.

Results vary run to run because the model samples; re-run to confirm a figure.

## How token usage is measured

The metric is **tokens that enter the main agent's context** to reach the same
answer (the file locations). The main agent is Claude, so the most appropriate
counter is Anthropic's own — used automatically when `ANTHROPIC_API_KEY` is set
(`pip install anthropic`). Without a key it falls back to a local `tiktoken`
encoding (`pip install tiktoken`), then to a chars/4 estimate. Each report names
the tokenizer it used. Absolute counts shift between tokenizers; the ratio
between arms does not.

`token_usage.py` compares three numbers per query:

- **WITH FastContext** — the exact JSON the MCP tool returns to the agent
  (citations, final answer, metadata). That is everything the main agent
  ingests for the lookup.
- **WITHOUT, inline search** — the tool-result bytes in FastContext's own
  trajectory: the identical search work, counted as if the main agent had run it
  itself and read every result into context. This is the apples-to-apples
  baseline.
- **WITHOUT, grep + read** — an independent baseline: grep the repo for sensible
  terms and read every matching file.

Only answered queries count toward the reported reduction. A miss "saves" tokens
but returns nothing, so it is not a saving.

## Tuning notes

Things that moved accuracy on this set:

- **`FC_TEMPERATURE`.** FastContext defaults to 0.7, which is high for a
  deterministic locate task — the search path wanders and sometimes answers off
  a loose grep hit. Over three iterations the file-hit rate was 12/15 (80%) at
  0.7 versus 14/15 (93%) at 0.2, with fewer tool calls. The benchmarks default
  to 0.2.
- **`FASTCONTEXT_REROOT_PATHS`.** The model truncates paths in some citations
  even at full precision; re-rooting recovers them. Leave it on.

`accuracy.py` honours `BENCH_ITERS` (default 1). Use a few iterations to average
out sampling noise before trusting a single number.

## Caveats

- This measures context cost, the mechanism behind the savings, not Claude's
  billing meter directly. The ground-truth figure is a real Claude Code A/B:
  run one task told to use `fastcontext`, the same task told to only grep, and
  compare `/cost`.
- The cases are written against this repo. Benchmarking another codebase means
  writing cases for it (set `FASTCONTEXT_BENCH_REPO`).

## Comparing hardware / precision

Set `BENCH_LABEL` to write results under `results/<label>/` instead of the top
level, so runs against different endpoints don't overwrite each other:

```bash
BENCH_LABEL=8gb-a2000-quant BASE_URL=http://127.0.0.1:30001/v1 python benchmarks/accuracy.py
BENCH_LABEL=24gb-full       BASE_URL=https://gpu24/v1          python benchmarks/accuracy.py
```

## Experiment log

[EXPERIMENTS.md](EXPERIMENTS.md) records what we have tried, the results, and
the resulting defaults.

## Latest results

- **End-to-end A/B (does it help the main agent?):** [ab/RESULTS.md](ab/RESULTS.md)
  — the 2×2 above.
- **Large-repo locator + context/precision sweeps:** [maximkeep/results/FINDINGS.md](maximkeep/results/FINDINGS.md).
- **Isolated locator, per hardware/precision config:** `results/8gb-a2000-quant/`,
  `results/12gb-3060-full/`, and the cross-config comparison in
  [EXPERIMENTS.md](EXPERIMENTS.md) (experiments 6–8).

Key tuning + serving findings from those runs (all in EXPERIMENTS.md): lower
`FC_TEMPERATURE` to 0.2 (80% → 93%); keep `FASTCONTEXT_REROOT_PATHS=1`; Q4_K_M is
the sweet spot (Q6 is worse and slower); **never quantise the KV cache** (`q4_0`
KV badly degrades tool-calling); Ollama-GGUF matches vLLM on a capable card.
