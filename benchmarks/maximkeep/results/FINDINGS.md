# Large-repo matrix findings — Maxim Keep

## Repo sizes (why "small" vs "large" matters here)

| repo | tracked files | code files | lines of code |
|---|---|---|---|
| `fastcontext-agent-tools` (upstream bench target) | 56 | ~20 | **~1.4k** (Python) |
| **Maxim Keep** (`sasystem`, this set) | 2,019 | ~1,360 | **~433k** (C# 222k · Vue/TS 165k · JS 34k · SQL 12k) |

About a **300× difference in LOC**. The upstream small-repo accuracy (~93–100%)
and this repo's (~30–44%) are not measuring the same difficulty regime — the gap
is the codebase size, not the harness. (LOC = `git ls-files` per language × `wc -l`,
so it counts committed source, excluding vendored/build dirs.)

## AUTHORITATIVE RESULT (2026-06-29, big card, iters=10)

Run on a faster/larger GPU (`192.168.0.22`, ~12 s/query vs ~60–90 s on pve-3), Q4
`fc-q4-nothink-{16,64,96,128}k`, t6, **`BENCH_ITERS=10` = 100 attempts/cell** — enough
to beat the sampling noise that made the earlier iters=3 numbers (below) untrustworthy.

| num_ctx | file-hit | timeouts |
|---|---|---|
| **16384** | **43/100 (43%)** | 6 |
| 65536 | 28/100 | 11 |
| 98304 | 37/100 | 7 |
| 131072 | 37/100 | 4 |

**Conclusion: a larger context window does NOT improve accuracy on this large repo.**
16k scored highest; 64k/96k/128k were equal or worse. Per-query: only q1
(`RequireTenantIntegration`) clearly benefited from more context (5→10); q8
(`integrations.ts`) *decayed with context* (3→0 at 128k — more committed design-`.md`
decoys pulled into the window); q4 (`TenantIntegrationSettings`) is 0/10 in EVERY config
(always mis-cites Azure AI services). The limiter is per-query difficulty / the 4B model's
agentic competence, **not** the window size. The "large repos need a bigger window"
hypothesis is not supported. (For precision — which *does* move the needle at 64k —
see the next section.)

## PRECISION × CONTEXT (2026-06-29, big card, iters=10, 100 attempts/cell)

Ran the Q8 and fp16 GGUFs (`fc-q8/f16-nothink-{16,64}k`) with the same settings
as the Q4 cells above, plus a Q4@64k **re-run** as a control, to fill the 2×2
precision × context grid:

| file-hit /100 | 16k | 64k |
|---|---|---|
| **Q4** | 43 | 28, **32** (re-run) → ~30 |
| **Q8** | **38** | **44** |
| fp16 | — | **44** |

- **fp16 buys nothing over Q8 (44 = 44).** Never ship above 8-bit.
- **It's a precision × context interaction, not "Q8 is better."** At **16k, Q4 ≥ Q8**
  (43 vs 38 — within noise, a tie); at **64k, Q8 ≫ Q4** (44 vs ~30). The mechanism:
  **Q4 degrades as context grows (43 → ~30) while Q8 holds (38 → 44).** Higher
  weight precision is a defence against large-context degradation, not a free
  accuracy boost.
- **The competence ceiling is unchanged (~43–44).** Both the best Q4 config
  (16k = 43) and the best Q8 config (64k = 44) top out there. No precision or
  context knob breaks past it — the limiter is still the 4B model's agentic
  competence, as the context section concluded.
- **Confidence:** the 64k column replicates on both sides (Q4 28/32 over two runs;
  Q8 and fp16 both exactly 44), so the 64k gap is solid. The 16k Q4-vs-Q8 (43 vs
  38) is single-run each and within sampling noise — treat as "tied", not "Q4 wins".
- This **refines** upstream exp 6 (Q6 *hurt* on the small repo at 16k): precision
  is neutral-to-negative at small context/easy tasks, and helps only by preventing
  large-context decay on a hard repo.
- Per-query: q4 (`TenantIntegrationSettings`) stays 0/10 at *every* precision and
  context (mis-cites Azure/migration files) — the persistent hard failures are a
  query/decoy problem, untouched by precision. Still the bigger gap to fix.

**Practical:** there's no reason to switch precision for accuracy alone — at the
contexts that fit a given card, Q4 is competitive. The only case for Q8 is if you
*must* run a large context (64k) on a ≥24 GB card, where it avoids Q4's
large-context degradation (~+14 pts, back to the ~44 ceiling). On smaller cards
(16k), Q4 is the right choice.

## EXACT vs AREA — is it a useful navigator even when it misses the file?

Re-scored the Q8@16k run (same 100 attempts) crediting an **area-hit** = any
citation in the *same directory* as the ground-truth file ("right neighbourhood"),
alongside the usual **exact-hit**. Tests whether the tool is still useful as a
locator when it doesn't nail the exact file.

| metric | rate |
|---|---|
| exact-hit | 39/100 |
| area-hit (same dir) | 51/100 |

- Only **+12 points**, and **q9 alone is +7** (exact 1/10 → area 8/10: the MCP
  reMarkable handlers cluster in one folder, so it finds the neighbourhood without
  the exact file). q4 +2, q8 +2, q1 +1; the other six queries have **area = exact**
  (miss the file → miss the area entirely).
- So the "still useful when not exact" effect is **real but not general** — it
  appears only when a feature's files happen to sit in one directory, not across
  query shapes. Even with the generous same-directory credit, it's ~half on a
  433k-LOC repo.
- Verdict: on a large repo this is a coin-flip-to-half locator, not a reliable
  one. The navigator framing rescues specific query types, not the tool overall.
  (The only measurement that would settle real-world value is an end-to-end A/B —
  main agent solving tasks with vs without FastContext, comparing cost + success —
  which has not been run.)

---

# (earlier, iters=3 on pve-3 — kept as the cautionary tale)

# Large-repo matrix findings — Maxim Keep (2026-06-28)

Private corpus (see ../README.md). 10 queries, `BENCH_ITERS=3` (30 attempts/cell),
temp 0.2, reroot on, retry-on-empty, model `fc-q4-nothink` GGUF on pve-3 (24 GB).

## All cells

| cell | num_ctx | max_turns | timeout | file-hit |
|---|---|---|---|---|
| mk-16k-t6        | 16384 | 6  | 300s | 8/30 (27%) |
| mk-32k-t6        | 32768 | 6  | 300s | 14/30 (47%) |
| **mk-32k-t6-600** (re-run) | 32768 | 6 | **600s** | **8/30 (27%)** |
| mk-16k-t12       | 16384 | 12 | 300s | 12/30 (40%) |
| mk-32k-t12       | 32768 | 12 | 300s | 11/30 (37%) |
| mk-48k-t6-600    | 49152 | 6  | 600s | 11/30 (37%) |

## Headline: variance dominates — no context/turn effect is established

The pivotal observation is the **re-run**: `32k/t6` scored **14/30 then 8/30 on
identical settings** (the second run even had a *more* generous 600s timeout, which
should only help). A 6/30 (~20-point) swing on the same config.

Every cell sits in an **8–14/30 band**, and a single config (`32k/t6`) spans that
whole band by itself. So the run-to-run sampling noise at `BENCH_ITERS=3` is **larger
than any difference between 16k / 32k / 48k or t6 / t12**. An earlier draft of this
file concluded "context nearly doubles accuracy, adopt 32k" — that was reading a lucky
sample as signal. **Retracted.** From this data we cannot conclude that a larger
context window helps *or* hurts on this repo.

This matches the upstream caveat (EXPERIMENTS.md): the query set is small and
sampling-noisy; iters=3 is not enough to separate close configs. Separating an effect
of this size would need far more iterations (≈10–20/query) and probably more queries —
a multi-hour run, worth it only if the question is worth that.

## What IS robust

1. **Large repos are much harder, full stop.** ~27–47% here vs ~93–100% on the small
   upstream repo at the same settings. The window size isn't what closes that gap.
2. **A hard failure floor independent of config:** q4 (`TenantIntegrationSettings` —
   consistently mis-cites Azure AI services) is 0/3 in *every* run; q8 (`integrations.ts`)
   is 0/3 in most; q9/q10 are erratic. These look like query-phrasing / decoy problems
   (the repo's own committed design `.md` docs are decoys for "integration" queries), not
   context problems — and are the more promising thing to fix.
3. **The dominant lever is the calling agent, not the model config:** because variance is
   this high, "re-run / cross-check / don't trust a single citation" buys more than any
   num_ctx change. (Same conclusion the confidently-wrong analysis reached.)

## Recommendation

- **Do not change the default or ship 48k on this evidence** — the differences are within
  noise; 48k (11/30) is below the lucky 32k sample and equal to the rest.
- If the context question matters enough to settle: re-run the matrix at `BENCH_ITERS≥10`
  (accept the multi-hour cost) so the confidence interval drops below the ~6/30 effect.
- Otherwise, invest in the robust gaps instead: the persistent q4/q8 misses (decoy/phrasing)
  and the agent-side re-run/verify workflow.

## Notes

- The `avg tool calls` column is invalid (all explores in one run share a trajectory file
  keyed on the parent PID); cosmetic, does not affect file-hit.
- Timeout-misses still occur even at 600s on the heaviest queries — included as misses.
