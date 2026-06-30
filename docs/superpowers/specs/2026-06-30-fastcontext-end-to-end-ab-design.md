# Spec — FastContext end-to-end A/B (locate, large repo)

Date: 2026-06-30. Status: design, pending implementation.

## Decision this serves

A go/no-go: **is FastContext worth using on large repos?** Small/medium repos are
already settled (it's accurate and cheap there). The open question is the large-repo
case, where the 4B locator scores only ~40–50% file-hit in isolation. We measure the
thing that actually matters — whether the **main agent (Opus)** reaches the right file
**more cheaply** with FastContext than with its own grep/read — and present the
cost-vs-success **trade** per task for the user to judge. No fixed pass bar.

This is **Approach A (locate-only)**: the cheap controlled instrument. It is a leading
indicator, not the full end-to-end story (a locate-then-act A/B with test verification
would be Approach B, only if A is ambiguous).

## Experiment

- **Repo:** sasystem (Maxim Keep), ~433k LOC. The realistic large-repo case.
- **Tasks:** the 10 locate queries in `benchmarks/maximkeep/cases.py`, with existing
  hand-verified ground-truth files.
- **Arms (same Opus model, same repo, same query):**
  - **WITHOUT (baseline):** stock Claude Code, native `Grep`/`Glob`/`Read` only.
  - **WITH:** same + the `fastcontext_explore` MCP tool and the "delegate exploration
    first" directive (the recommended setup); may fall back to grep (realistic).
- **N:** start at 1 per task per arm for the first batch (cost gauge); decide the full N
  (target 5) after reviewing the first 10 runs.

## Metrics (per run)

- **Cost:** main-model tokens (input/output) + `total_cost_usd` from the headless JSON.
  This is the resource that matters; the 4B explorer's own tokens run on local GPU and
  are noted only as a footnote.
- **Success:** the ground-truth basename appears in the final answer. Also record
  "right directory" (the area metric).
- **Turns**, **wall-clock**.
- **tool_used (WITH arm):** whether the run actually called `fastcontext_explore`.
  Runs that ignored the tool are flagged and excluded from the headline — otherwise the
  arms are secretly identical and the comparison is void.

## Harness

One fresh headless Claude session per (task × arm × run):

```
claude -p "In this repository, find the file that implements: <query>. Report the file path(s)." \
  --model opus --output-format json [arm flags]
```
run with cwd = the sasystem checkout.

- **WITHOUT flags:** `--allowedTools Grep Glob Read Bash`, no MCP.
- **WITH flags:** `--mcp-config fastcontext.json` (MCP → gpu-24 `fc-q8-nothink-64k`)
  + `--append-system-prompt <delegate-first directive>` + fastcontext tool in
  `--allowedTools`.

Parse each run's JSON for `result`, `usage`, `total_cost_usd`, `num_turns`, and the
message log (for the tool_used flag). Write one row per run (CSV/JSON), then aggregate
into a per-task trade table (median tokens + success %, WITH vs WITHOUT) in a results
`.md`, flagging any task where the arms overlap within noise.

### Controls
- Fresh session per run; identical model/repo; interleave arm order.
- Pre-warm `fc-q8-nothink-64k` on gpu-24 so a cold load doesn't distort the first WITH run.
- Both arms equally exposed to Anthropic prompt-caching.

### WITH-arm config
- Endpoint: `http://192.168.0.248:11434/v1` (gpu-24; DHCP — re-confirm IP at run time),
  model `fc-q8-nothink-64k:latest`, `API_KEY=ollama`, `FC_TEMPERATURE=0.2`,
  `FASTCONTEXT_REROOT_PATHS=1`, `FASTCONTEXT_EXPLORE_RETRIES=2`.

## Phasing & cost gate

The main agent is **Opus**, so this experiment spends real, non-trivial money (unlike
the cheap 4B locator benchmarks). Staged, with a stop after each step:

1. **Smoke test (2 runs):** one task, both arms. Verify headless `claude -p` reports
   per-run token usage reliably and the MCP/allowed-tools toggle works, and that the
   tool_used flag is detectable. **If usage numbers aren't trustworthy, stop — the
   instrument is invalid and we rethink.**
2. **First batch (10 runs):** 5 tasks × 2 arms × N=1. Print real per-run + projected
   full cost, and a preview trade table. **Review with the user**: decide N and whether
   to run the full set.
3. **Full run:** remaining tasks at the chosen N.

A per-run turn/token cap guards against runaway sessions.

## Risks & honesty

- **Locate-only flatters/under-sells.** It's the tool's exact job and doesn't capture
  whether locating helps the downstream fix. Treat the result as a leading indicator;
  escalate to Approach B only if A is ambiguous.
- **The agent may ignore the tool.** Mitigated by the directive + allow-list, and made
  visible by the tool_used flag.
- **Noise.** Opus is non-deterministic; N=1 in the first batch is a cost gauge only, not
  a verdict. The headline needs the fuller N.
- **Build risk:** the headless-usage-reporting capability is load-bearing; verified in
  step 1 before any scale spend.
- **Endpoint availability:** gpu-24 is a laptop on DHCP; confirm reachable + warm before
  the WITH arm.

## What the result looks like

A per-task table — WITH vs WITHOUT on (median main-model tokens, success %, turns) — plus
an overall summary. The expected crux it exposes: because the locator is right only
~40–50% on big repos, does delegate-first net a token saving, or do the misses (tool call
**then** grep-fallback) make WITH cost *more* than just grepping? The user reads the trade
and decides keep/drop.
