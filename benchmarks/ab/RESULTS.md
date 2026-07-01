# End-to-end A/B — when is FastContext worth running? (main-agent strength × repo difficulty)

> Started as "does it help Opus on a large repo?" and grew into a 2×2 across
> main-agent strength and repo difficulty. The headline is the 2×2 near the
> bottom; the sections below build up from the first (Opus, large repo) arm.

Date: 2026-06-30. Harness: `benchmarks/ab/` (this directory). Spec:
[../../docs/superpowers/specs/2026-06-30-fastcontext-end-to-end-ab.md](../../docs/superpowers/specs/2026-06-30-fastcontext-end-to-end-ab.md).

## The question

Earlier work measured the FastContext locator *in isolation* (~40–50% file-hit on a
large repo, ~93–100% on a small one). That can't answer the question that decides
adoption: does a coding agent solve tasks better or cheaper *with* FastContext than
without? This is the end-to-end test, scoped to the case the decision actually hinges
on — **large repos** (small/medium were already a clear yes).

## Setup

- **Main agent:** Claude **Opus**, run headless (`claude -p --output-format stream-json`).
- **Repo:** sasystem / Maxim Keep, ~433k LOC (.NET + Vue/TS + JS).
- **Tasks:** 10 "where is X" locate queries with hand-verified ground-truth files
  (`../maximkeep/cases.py`). This is locate-only (Approach A) — it measures finding the
  file, not the downstream fix.
- **Arms (identical except the tool):**
  - WITHOUT — native `Grep`/`Glob`/`Read` only.
  - WITH — plus the `fastcontext_explore` MCP tool (gpu-24, `fc-q8-nothink-64k`) and a
    "delegate exploration first" directive; may fall back to grep.
  - Isolation enforced with `--strict-mcp-config` + `--disallowedTools
    ToolSearch,Skill,Task,Agent` so the WITHOUT arm cannot reach FastContext by any path.
- **N = 5** per task per arm = **100 runs**. Cost is `total_cost_usd` from each run
  (authoritative; includes cached repo-context reads). Total spend **$27.94**, 0 errors.

## Result

| | WITHOUT (Opus greps) | WITH (FastContext) |
|---|---|---|
| Success | **47/50 (94%)** | **47/50 (94%)** |
| Total cost | $14.47 | $13.47 |
| FastContext actually used | 1/50 | 49/50 |

**Success is identical. Cost is within ~7%** ($1 over 50 runs) — too small and too noisy
to count as a saving. With a strong main agent, the 4B locator neither finds more nor
meaningfully reduces cost on this repo.

### Per-task — it reshuffles difficulty rather than lifting the floor

| query | WITHOUT | WITH | note |
|---|---|---|---|
| t6 `FeatureProfileService` | 5/5 | **2/5** | FastContext **hurt** — Opus trusted a confident wrong citation and didn't recover |
| t1, t4, t10 | 4/5 | 5/5 | FastContext **helped** — steered Opus to a file it otherwise missed once |
| t2, t3, t5, t7, t8, t9 | 5/5 | 5/5 | no difference |

Each arm loses 3 of 50, in *different* places, and they cancel. The standout is **t6**:
delegating introduced a failure mode — a plausible-but-wrong citation the main agent
believed — that pure grep never hit. That is a real downside, not just absence of benefit.

The first-10 smoke batch (5 queries, N=1, $3.02) showed the same shape: 5/5 both arms,
cost tied — consistent with the full run.

## Verdict (this arm: Opus × large repo)

**On large repos with a strong (Opus) main agent, FastContext is not worth running.** No
success gain (94% either way), negligible cost change, and a genuine risk of being misled
by a confident wrong citation. (The full picture across agents and repo sizes is the 2×2
below.)

## Caveats

- **Locate-only.** Measures finding the file, not whether FastContext helps Opus *fix*
  things end-to-end. A locate-then-act A/B (test-verified) would be the fuller test; this
  locate result is a strong prior that it won't flip the call.
- **N=5** firms the aggregate (50/arm) but per-task deltas (5/5 vs 2/5) are small-sample —
  directional, not precise.
- **One isolation leak:** 1/50 WITHOUT runs reached FastContext despite the disallow; it
  does not move the 94%/cost aggregate, but the isolation is not airtight.

## The 2×2 — main-agent strength × repo difficulty

The counterweight to the Opus run: rerun the A/B with a **weak main agent** — the local
`Qwen3.6-35B-A3B` (Q4 GGUF) driving `claude -p` via an Anthropic-compatible endpoint
(`pve-3:8080`), same WITH-arm explorer (gpu-24 `fc-q8-nothink-64k`), same isolation. Then
both agents on both the large repo (10 queries) and this small repo (5 queries), N=5.

**File-hit rate, WITHOUT → WITH FastContext:**

| main agent | small repo (this repo, easy) | large repo (sasystem, hard) |
|---|---|---|
| **Opus** (strong) | 100% → 100% (wash) | 94% → 94% (wash) |
| **Qwen-35B** (weak) | 100% → 100% (wash) | **60% → 66%** (+6 pts) |

**FastContext moves the needle in exactly one cell: weak agent × hard repo.** Everywhere
else it is a wash — a strong agent doesn't need it (either repo), and an easy repo leaves
no room (either agent). The value tracks the *main agent's need*, not the locator's
standalone accuracy — which is why the isolated-locator numbers (great on small, ~40–50%
on large) were the wrong lens.

Detail on the one cell that helps (Qwen × large, N=5, 100 runs, 0 errors):
- Success 60% → 66%. Helped t3 (1→3), t5 (2→3), t10 (3→5); hurt t4 (4→3), t9 (3→2).
- The lift is **directionally consistent** across three independent passes (batch +1/5,
  wide +2/10, N=5 +3/50) — that consistency, not the single N=5 delta, is what makes it
  credible; a single cell's 60-vs-66 confidence interval overlaps.
- It **costs time, not saves it.** WITH used more turns (median 5.5 vs 5.0) and ~47% more
  wall-clock (99 vs 67 min). An early "FastContext leashes the model's overthinking" idea
  did not survive the wider sample — the one apparent speed-up was a single 900 s timeout
  the unaided agent hit and the aided one avoided, not a general effect.

## Overall verdict

**Run FastContext in proportion to how much the driving model needs it.** Under a frontier
main agent it's redundant regardless of repo; on an easy repo it's redundant regardless of
agent. It earns its keep only for a **weak/local main agent on a large, hard codebase**, and
even there the gain is modest (~+6 pts) and comes at a latency cost — worth it when API
budget forces a small local driver, not worth it under Opus. The strong small/medium-repo
locator value (isolated ~93–100%, ~25× context saving) is a separate, still-valid point
about the locate phase in isolation; it does not imply an end-to-end win.

## Caveats
- **Locate-only** (Approach A): measures finding the file, not the downstream fix.
- **N=5 per cell**; per-cell deltas are within sampling noise — the weak-agent lift rests on
  cross-pass consistency, not one number.
- **One isolation leak** (1/50 in one Opus-large WITHOUT run) — doesn't move aggregates.
