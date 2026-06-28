# Experiment log

A running record of the tuning experiments behind the defaults in this repo.
Each entry states the question, the method, the result, and the decision. The
benchmark scripts that produced these live alongside this file; latest numbers
are in [results/](results/).

All runs used the `FastContext-1.0-4B-RL` model on a full-precision endpoint
(remote 12 GB card over an SSH tunnel) unless noted. The test set is five
"where is X" queries (`cases.py`) with answers known in this repo's own source,
so it is small and sampling-noisy — single-pass numbers vary, and figures below
use multiple iterations where it matters. Re-run to confirm.

## Diagnosis: how the misses fail

The wrong/missing citations are **sampling variance**, not a broken prompt. Two
distinct failure modes, which matter for the fixes:

- **Empty / weak** — the run returns no citation (or only citations the
  validator rejects). Detectable from a single run.
- **Confidently wrong** — the run cites a plausible but wrong file with no
  warnings. Indistinguishable from a good run on its own; only visible as
  disagreement across repeated runs.

The vendored system prompt also tells the model to be a "fast agent that returns
output as quickly as possible" (twice), which biases it toward answering before
verifying.

## Experiments

### 1. Path re-rooting (`FASTCONTEXT_REROOT_PATHS`) — adopted

- **Question:** the model sometimes truncates the workspace path in citations
  (`/mnt/.../repo/x` → `/repo/x`), which the validator then rejects. Does
  re-rooting recover them, and is it only needed for quantised models?
- **Method:** file-hit rate with the flag off vs on.
- **Result:** 3/5 → 5/5. The truncation happens even at full precision, not just
  under 4-bit quantisation. Re-rooting is a no-op on already-correct paths.
- **Decision:** default **on** at any precision.

### 2. Token usage: with vs without FastContext — informational

- **Question:** how much main-agent (Claude) context does delegating save?
- **Method:** `token_usage.py`. Per query, tokens that enter the main context
  WITH FastContext (the returned JSON) vs WITHOUT (the tool-result bytes in the
  explorer's own trajectory = the same search done inline; and an independent
  grep+read baseline). Tokenizer: `tiktoken o200k_base` (Anthropic's counter
  when `ANTHROPIC_API_KEY` is set).
- **Result:** ~1.6k tokens into context across answered queries vs ~43k doing
  the search inline — roughly **25–27× less context** for the locate phase.
- **Decision:** n/a (this quantifies the value, it is not a knob).

### 3. Sampling temperature (`FC_TEMPERATURE`) — adopted

- **Question:** FastContext defaults to 0.7. Is that too high for a
  deterministic locate task?
- **Method:** `accuracy.py` with `BENCH_ITERS=3` (15 attempts) at 0.7 vs 0.2.
- **Result:** **12/15 (80%) at 0.7 → 14/15 (93%) at 0.2**, with fewer tool calls
  and a more deterministic search path (a flaky query went byte-identical across
  three runs at 0.2).
- **Decision:** default **`FC_TEMPERATURE=0.2`**.

### 4. "Verify before cite" prompt addition — rejected

- **Question:** does instructing the model to open a file and confirm the symbol
  is *defined* there (not just referenced) before citing improve accuracy?
- **Method:** A/B in `build_fastcontext_prompt`, gated behind an env var,
  `BENCH_ITERS=3` at temperature 0.2.
- **Result:** **12/15 with and 12/15 without.** No net change, did not fix the
  target query, and slightly increased tool calls. The per-query differences
  were n=3 noise.
- **Decision:** **reverted.** No unproven prompt text shipped.

### 5. Self-consistency / cascade voting — adopted (retry-on-empty)

- **Question:** misses are variance, so repeating and combining runs should help.
  Should that apply to every query, or only where a cheap signal predicts a query
  is uncertain? Voting on already-reliable queries is wasted cost.
- **Method:** collected 6 independent attempts per query (30 total) recording hit
  and confidence signals (empty, warnings, max-turns, tool calls), then (a)
  checked whether misses carry a detectable signal, and (b) Monte-Carlo simulated
  strategies, scoring hit rate and average model-runs (cost).
- **Result — gate:** all **7/7 misses were empty** results (zero warnings,
  zero max-turns, zero confidently-wrong), and **0/23 hits** were false-flagged.
  So "no citations" perfectly predicts a miss on this set, with no wasted retries.
- **Result — strategies** (equal weight per query):

  | Strategy | Hit rate | Avg runs |
  |---|---|---|
  | single (baseline) | 76.7% | 1.0 |
  | **retry-on-empty (≤3)** | **88.2%** | **1.38** |
  | gate → union cascade | 88.1% | 1.47 |
  | blanket union of 3 | 88.4% | 3.0 |
  | blanket agreement ≥2/3 | 78.5% | 3.0 |

  Retry-on-empty matches blanket union's accuracy (+11.5 pts) at less than half
  the cost, and is 1.0x on queries that answer first time. Blanket agreement is
  *worse* — it filters out the rare correct citation on the flaky query.
- **Decision:** adopt **retry-on-empty**, `FASTCONTEXT_EXPLORE_RETRIES=2`
  (up to 3 attempts; only re-runs an explore that returned no citations; set 0 to
  disable). Implemented in `runtime.run_fastcontext`. Blanket voting rejected as
  not worth the cost; this confirms the adaptive approach over a uniform one.

### 6. Hardware / precision sweep — in progress

- **Question:** how do accuracy and context savings change with GPU and
  precision (4-bit quant on a small card vs full BF16)?
- **Method:** same five queries, temperature 0.2, re-rooting on, raw single-pass
  (`FASTCONTEXT_EXPLORE_RETRIES=0`), `BENCH_ITERS=3`. One endpoint per config;
  results under `results/<label>/`.
- **Result:**

  | Config | GPU | Precision | File-hit | Context reduction |
  |---|---|---|---|---|
  | `8gb-a2000-quant` | A2000 8 GB | 4-bit (bitsandbytes) | 11/15 (73%) | ~28x / 33x |
  | `12gb-3060-full` | RTX 3060 12 GB | full BF16 | 13/15 (87%) | ~13x / 20x |
  | `24gb-full` | 24 GB | full BF16 | _pending_ | _pending_ |

  4-bit quantisation costs roughly 14 points of accuracy versus full precision
  on the same model — the misses (and the path truncation re-rooting fixes) are
  worse under quant. Context reduction is large in both arms (>10x); the exact
  multiple is noisy because it depends on how much searching each run's
  trajectory happened to do, so treat it as order-of-magnitude.
- **Decision:** prefer full precision when the card allows it; the 8 GB quant
  path is a usable fallback at a real accuracy cost. 24 GB column pending an
  endpoint.

## Config decisions so far

| Setting | Value | Why |
|---|---|---|
| `FASTCONTEXT_REROOT_PATHS` | `1` | Recovers truncated citation paths (exp. 1). |
| `FC_TEMPERATURE` | `0.2` | 80% → 93% hit rate, fewer tool calls (exp. 3). |
| `FC_MAX_TOKENS` | `4000` | Fits prompt+output under a small `CTX_LEN`; final answers are short. |
| `FASTCONTEXT_EXPLORE_RETRIES` | `2` | Retry-on-empty recovers ~11 pts of hit rate at ~1.4x cost (exp. 5). |

## Caveats

- The five-query set is small and written against this repo; treat absolute
  numbers as indicative, not a leaderboard.
- Token figures measure context cost (the mechanism). The ground-truth value
  number is a real Claude Code A/B comparing `/cost` on a task with and without
  the tool.
