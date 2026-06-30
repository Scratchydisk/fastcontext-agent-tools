# End-to-end A/B — does FastContext help a strong main agent on a large repo?

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

## Verdict

**On large repos with a strong (Opus) main agent, FastContext is not worth running.** No
success gain (94% either way), negligible cost change, and a genuine risk of being misled
by a confident wrong citation. This does **not** contradict the small/medium-repo finding
(strong there, ~25× context saving for the locate phase) — it says that value doesn't
transfer to the large-repo + strong-driver regime.

## Caveats

- **Locate-only.** Measures finding the file, not whether FastContext helps Opus *fix*
  things end-to-end. A locate-then-act A/B (test-verified) would be the fuller test; this
  locate result is a strong prior that it won't flip the call.
- **N=5** firms the aggregate (50/arm) but per-task deltas (5/5 vs 2/5) are small-sample —
  directional, not precise.
- **One isolation leak:** 1/50 WITHOUT runs reached FastContext despite the disallow; it
  does not move the 94%/cost aggregate, but the isolation is not airtight.

## Next experiment — the opposite extreme

The obvious counterweight: replace the strong main agent with a **weak one** — a small
(~30–35B) *local* coding model (e.g. `qwen3-coder:30b`, `devstral-small-2:24b`) driving
the same 10-query A/B. Hypothesis: a weaker main agent is a worse locator on its own, so
delegating to the trained 4B explorer may *lift* it — meaning FastContext's value could
depend on main-agent strength (redundant under Opus, useful under a small local model).
Attractive cost profile too: a local main agent is ~$0 in API spend (just GPU time),
unlike this run's $28 of Opus.

This is **not** a plain `--model` swap, though: `claude -p` drives Anthropic models, not
an Ollama endpoint. Making a local 35B the *main agent* needs an Anthropic-compatible
proxy in front of Ollama (e.g. LiteLLM) with `ANTHROPIC_BASE_URL` pointed at it — or a
different agent runner entirely. The arm logic in `arms.py` (isolation flags, WITH/WITHOUT)
is reusable; the main-model routing is the new piece, and worth designing deliberately
(its own spec) rather than bolting on.
