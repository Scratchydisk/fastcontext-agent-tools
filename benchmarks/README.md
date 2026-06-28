# Benchmarks

Two small benchmarks for the FastContext explorer:

- `accuracy.py` — does it cite the right files?
- `token_usage.py` — how much main-agent context does it save versus searching
  inline?

Both run a fixed set of "where is X" questions (`cases.py`) whose answers are
known in this repository's own source, so this repo is the corpus.

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

Per hardware/precision config:

- 8 GB, 4-bit quant: [results/8gb-a2000-quant/](results/8gb-a2000-quant/)
- 12 GB, full BF16: [results/12gb-3060-full/](results/12gb-3060-full/)

See [EXPERIMENTS.md](EXPERIMENTS.md) (experiment 6) for the cross-config
comparison.
