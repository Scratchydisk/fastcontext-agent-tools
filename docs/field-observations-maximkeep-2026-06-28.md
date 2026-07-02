# FastContext — field observations (Maxim Keep repo, 2026-06-28)

Notes from heavy real-world use of the FastContext MCP against the **Maxim Keep**
.NET 10 + Nuxt 3 monorepo during a large feature build. (Maxim Keep is a **private
repo**, not available to other users; recorded here for the findings — the code
itself is not bundled.)

> **Reconciled against [`benchmarks/EXPERIMENTS.md`](../benchmarks/EXPERIMENTS.md).**
> An earlier draft of this file recommended a Q6 model and a larger `num_ctx`. Both
> are **contradicted by the repo's own benchmarks** and have been retracted below.
> Keeping the corrected reasoning so the mistake isn't repeated.

## Setup in use
- Endpoint: Ollama on `pve-3` (`192.168.0.4:11434`, a 24 GB card — matches the
  `24gb-5090` bench configs). Model `fc-q4-nothink-16k:latest` (FastContext-1.0-4B-RL,
  Q4_K_M, `num_ctx 16384`). CLI tuning already at the adopted defaults: `FC_TEMPERATURE=0.2`,
  `FASTCONTEXT_REROOT_PATHS=1`, `FASTCONTEXT_EXPLORE_RETRIES=2`, `FC_MAX_TOKENS=4000`.
- Modelfile note: the fc models were pulled from HF GGUF (`hf.co/rocketsvm/…Q6_K`,
  `hf.co/mitkox/…Q4_K_M`) and aliased — there is **no authored `*.modelfile`** for them in
  `/mnt/data-sas/home/stewart/ollama/`. The Modelfile bakes `temperature 0.6`; the CLI's
  `FC_TEMPERATURE=0.2` override is what's actually applied (good — Exp 3).

## What worked
- Fast neighbourhood-finding: a vague query ("where are the daily briefing defaults
  configured") still surfaced the right **file** (`BriefingController.cs`) on the first call.
- Re-rooting + low temp behaved as the adopted defaults intend.

## Problems observed (and how they map to EXPERIMENTS.md)
1. **`fastcontext_health` is misleading — it never calls the model.** It reports `ok: true`
   on env presence alone. Twice this session it reported healthy while the endpoint actually
   returned `404 model not found` (a stale `MODEL` / wrong base URL during live reconfig) and
   the explore failed. This is the one clearly-actionable gap and is **not** covered by any
   existing experiment.
2. **A single confident citation was flat wrong.** A query returned exactly one citation —
   `usePulseSettings.ts` (the **Pulse** feature), not Briefing — and mis-described the field
   (`soundEnabled` reported as `enabled`). This is precisely the **"confidently wrong"**
   failure mode EXPERIMENTS.md flags as the hard one: *"indistinguishable from a good run on
   its own; only visible as disagreement across repeated runs."* Note **retry-on-empty (Exp 5)
   does NOT catch this** — that mechanism only re-runs *empty* results; a confident wrong
   answer sails through. So this mode remains unmitigated except by repeated runs / human
   verification.
3. **Phrasing finesse didn't help.** A deliberately "sharpened" query did *worse* than the
   loose original (it produced the Pulse miss). Consistent with Exp 4 ("verify before cite"
   prompt change → no net gain): wording/prompt tweaks are dominated by sampling variance on
   a 4B model.
4. **Near-miss on exact lines.** The briefing query cited the *update* endpoint
   (`BriefingController.cs:245-278`) rather than the *defaults* (`:437-446`). Right file,
   wrong lines — fine for a locator, but the exact answer needed verification.

## Retracted suggestions (disproven by EXPERIMENTS.md)
- ~~Switch to the Q6 model.~~ **Wrong.** Exp 6: Q6_K is worse than Q4_K_M on every card and
  slower. Q4_K_M is the sweet spot; the limiter is the 4B model's agentic competence, not
  quant precision. **Stay on Q4.**
- ~~Raise `num_ctx` to 32k/64k for accuracy.~~ **Not an accuracy lever.** Exp 8: ctx64k = 12/15
  vs 14/15 at 16k (noise). Exp 2: the explorer's trajectory already runs ~43k while scoring
  14/15 at `num_ctx 16384`, so the model copes with trajectory > context. The Maxim Keep deep
  explores I saw (60k–126k-token trajectories) are bigger because it's a bigger repo, but the
  evidence says that does **not** translate into needing a bigger window for accuracy.
  *Only* consider raising `num_ctx` if explores are observed to **fail to traverse** a large
  repo (a coverage problem, not accuracy) — and even then EXPERIMENTS.md Exp 8's guidance
  applies: "pick the context to match the repos you explore, not to chase accuracy." On this
  24 GB card ctx 65536 stays resident (~12 GB) if ever needed.

## Suggestions that still stand
1. **Make `fastcontext_health` actually probe** (the only solid one). Fire a 1-token
   completion against `MODEL`@`BASE_URL`; report `ok: true` only if it round-trips. Catches
   model-not-found / endpoint-down / wrong base URL — the exact failures seen today, which the
   env-only check hides.
2. **Workflow guidance for the calling agent** (the `/fastcontext` command), aimed at the
   *confidently-wrong* mode that no current experiment mitigates:
   - Treat a **single citation as low-confidence** — re-run (variance will disagree on a wrong
     hit) or cross-check before trusting it. This is the only lever against confidently-wrong,
     per the Exp 5 diagnosis.
   - **Verify by grepping a distinctive token** from the citation, not just opening the file —
     confirms the *concept* and catches feature collisions (Pulse↔Briefing).
   - Keep "candidates, not ground truth" framing; FastContext stays the fast first-pass locator.
3. **Optional tidy:** bake `temperature 0.2` into a Modelfile `PARAMETER` so the safe value
   holds even if the `FC_TEMPERATURE` env var is ever unset (belt-and-braces on Exp 3).

## Net
The config here is already on the research-backed optima (Q4, temp 0.2, reroot, retry-on-empty).
The only real defect surfaced this session is the env-only health check; the only real *quality*
gap is the confidently-wrong single-hit, which is a known, unmitigated failure mode best handled
by the calling agent re-running / verifying — not by quant or context changes.
