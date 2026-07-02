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

**Target-repo size:** this repo is small — 56 tracked files, ~1.4k lines of
Python — so a full exploration trajectory fits inside a 16k context. That is why
these numbers run high (~93–100%) and why context/precision knobs barely move
here. For the same experiments on a ~433k-LOC codebase (where they behave very
differently), see [maximkeep/results/FINDINGS.md](maximkeep/results/FINDINGS.md).

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

### 6. Hardware / precision / quant / context sweep

- **Question:** how do accuracy and context savings change with GPU, precision,
  quant level, and context length?
- **Method:** same five queries, temperature 0.2, re-rooting on. vLLM configs:
  raw single-pass, `BENCH_ITERS=3` (15 attempts). Ollama configs: retry-on-empty,
  `BENCH_ITERS=3` (15 attempts) on the capable cards, `BENCH_ITERS=2` (10) on the
  much slower P2000. Ollama runs use a no-think GGUF at `num_ctx 16384`
  (8192 on the P2000). One endpoint per config; results in `results/<label>/`.

  **Cross-GPU (vLLM):**

  | Config | GPU | Precision | File-hit |
  |---|---|---|---|
  | `8gb-a2000-quant` | A2000 8 GB | 4-bit bitsandbytes | 11/15 (73%) |
  | `12gb-3060-full` | RTX 3060 12 GB | full BF16 | 13/15 (87%) |
  | `24gb-full` | 24 GB | full BF16, ctx 65536 | 11/15 (73%) |

  **Ollama (GGUF, fp16 KV cache) on the capable cards:**

  | Config | GPU | Quant | File-hit |
  |---|---|---|---|
  | `8gb-a2000-ollama-q4` | A2000 8 GB | Q4_K_M | 14/15 (93%) |
  | `8gb-a2000-ollama-q6` | A2000 8 GB | Q6_K | 9/15 (60%, 1 timeout) |
  | `12gb-3060-ollama-q4` | RTX 3060 12 GB | Q4_K_M | **15/15 (100%)** |
  | `24gb-5090-ollama-q4` | RTX 5090 24 GB | Q4_K_M | 14/15 (93%) |

  **P2000 5 GB (Ollama GGUF — vLLM can't run on Pascal), quant × context:**

  | | ctx 8192 | ctx 16384 |
  |---|---|---|
  | Q4_K_M | 5/10 (50%) | timed out (>220 s/query) |
  | Q6_K | 3/10 (30%) | — (would time out) |

  Context reduction was >10x for every config (exact multiple noisy).

- **Findings:**
  - **Ollama Q4 GGUF matches or beats vLLM on a capable card.** Q4_K_M scored
    14/15 (A2000 8 GB), 15/15 (3060 12 GB), and 14/15 (5090 24 GB) — at or above
    the vLLM numbers on the same cards (11/15 and 13/15). So the GGUF path is not
    a second-class option on a card that *can* run vLLM; it's competitive across
    8–24 GB.
  - **The P2000's poor score was the card, not the GGUF.** The exact same Q4_K_M
    GGUF that scored 5/10 on the Pascal P2000 scored 14–15/15 on Ampere cards.
    Pascal's weakness (no flash-attn, slow, timeouts) is the limiter.
  - **Higher quant did not help — it hurt.** Q6_K was worse than Q4_K_M on every
    card (P2000 3/10 vs 5/10; A2000 9/15 vs 14/15) *and* slower (the A2000 Q6 run
    timed out on the heavy query). Q4_K_M is the sweet spot; the limiter is the
    small model's agentic competence, not quant precision.
  - **The cross-GPU vLLM configs are within sampling noise** — 24 GB full scored
    the *same* 11/15 as 8 GB 4-bit. The 11–13 spread is mostly q3 swinging.
  - **More context hurt on the weak card.** 16384 on the P2000 timed out per
    query; 8192 is its practical ceiling. On the Ampere cards 16384 was fine.
  - The P2000 needs Ollama + a community GGUF + a custom no-think Modelfile, and
    is much slower. Full write-up: [docs/running-on-pascal-p2000.md](../docs/running-on-pascal-p2000.md).

- **Decision:** for a card that can run vLLM, either engine works; Ollama with a
  Q4_K_M GGUF (fp16 KV cache — see exp. 7) is a strong, simple option. Avoid Q6
  (slower, no accuracy gain) and the Pascal/P2000 path (slow and weak).

### 7. Ollama KV-cache quantisation (`OLLAMA_KV_CACHE_TYPE`) — avoid it

- **Question:** Ollama/llama.cpp can quantise the KV cache (`q8_0`, `q4_0`) to
  save VRAM. Is `q4_0` KV a free memory win, or does it cost accuracy?
- **First (flawed) observation:** on the 12 GB 3060, whose ollama service ran
  `OLLAMA_KV_CACHE_TYPE=q4_0` **and** `OLLAMA_FLASH_ATTENTION=1` **and**
  `OLLAMA_NUM_PARALLEL=2`, FastContext returned **0/15**, vs 15/15 after removing
  those. That looked like "KV quant breaks tool-calling entirely" — but the
  comparison changed three env vars at once and was a single box on Ollama 0.30.6.
  **It was an overclaim.** A canary was run to isolate the variable.
- **Canary (clean single-variable):** RTX 5090, Ollama 0.30.11, same Q4_K_M GGUF,
  flash attention **on in every arm**, only the named variable changed,
  `BENCH_ITERS=3`:

  | Arm | KV cache | `NUM_PARALLEL` | File-hit |
  |---|---|---|---|
  | A | fp16 | 1 | 11/15 |
  | B | q4_0 | 1 | 6/15 |
  | C | q4_0 | 2 | 4/15 |

- **Result:** `q4_0` KV **degrades** agentic accuracy substantially — roughly
  halves the hit rate at parallel=1 (11→6) and is worse at parallel=2 (→4), with
  tool-call activity dropping sharply at each step (e.g. ~14–104 calls/query at
  fp16 vs ~3–31 at q4_0). It does **not**, on a modern Ollama, cause a total
  collapse on its own. The 3060's 0/15 was the extreme end of this gradient
  (q4_0 + parallel=2 + the older 0.30.6), not a clean "KV quant = 0" law. The
  single-run-per-arm numbers carry the usual 5-query noise, but the direction and
  the tool-call drop are consistent and corroborated.
- **Decision:** **don't quantise the KV cache for this workload.** It badly hurts
  agentic tool-use and worsens with parallel slots; the ~2 GB it saves is not
  worth it. Flash attention on its own (`OLLAMA_FLASH_ATTENTION=1`, fp16 KV) is
  fine. (Lesson logged: the original claim was confounded; a single-variable
  canary on independent hardware corrected it.)

### 8. Context window vs VRAM headroom on a 24 GB card

- **Question:** on a big card, can the model stay resident while leaving room for
  other work, and how far can the context be pushed before it stops fitting?
- **Method:** RTX 5090 24 GB, Ollama 0.30.11, `fc-q4-nothink` GGUF (fp16 KV,
  `OLLAMA_NUM_PARALLEL=1`). Loaded at increasing `num_ctx` and measured resident
  VRAM and GPU/CPU placement.
- **Result:**

  | `num_ctx` | Resident | Placement | Free of 24 GB |
  |---|---|---|---|
  | 16384 | 5.1 GB | 100% GPU | ~19 GB |
  | 32768 | 7.5 GB | 100% GPU | ~17 GB |
  | 65536 | 12 GB | 100% GPU | ~12 GB |
  | 131072 | 22 GB | 100% GPU | ~2.5 GB |
  | 262144 (max) | 43 GB needed | 45/55 CPU split | does not fit |

  KV cache costs ~150 KB/token (weights are a fixed ~2.5 GB). 131072 is the
  practical on-GPU ceiling on 24 GB; the model's full 262144 needs 43 GB and
  spills to CPU.
- **Accuracy at a large context:** `24gb-5090-ollama-q4-ctx64k` scored 12/15 vs
  14/15 at ctx 16384 — within sampling noise (the q2/q3 swing), i.e. no
  improvement and no clear penalty. Expected: this five-query repo fits in 16k,
  so extra context has nothing to do. Large contexts matter for exploring large
  repositories, not for accuracy on a small one.
- **Decision:** on a 24 GB card, ctx 65536 keeps the model resident (~12 GB) with
  ~12 GB free for other workloads; ctx 16384 leaves ~19 GB free. Pick the context
  to match the repos you explore, not to chase accuracy. `OLLAMA_NUM_PARALLEL>1`
  multiplies the KV cache, so account for it in the footprint.

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
