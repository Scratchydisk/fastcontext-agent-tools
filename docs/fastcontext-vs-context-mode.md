# Cutting Context Cost in Coding Agents: FastContext vs context-mode

*Findings note — Stewart McSporran, 16 June 2026*

> **Update, 2 July 2026:** the FastContext arXiv paper (2606.14066) was
> **withdrawn by the authors on 30 June 2026** (v4, no PDF served). The released
> 4B models and the analysis below stand; the benchmark tables cite specific
> versioned snapshots ([`v1`](https://arxiv.org/abs/2606.14066v1)), which remain
> readable, but the authors no longer endorse the paper's claims. Read the
> headline figures accordingly.

## TL;DR

Two tools sit under the banner of "fix the context problem," and they feel like
rivals. They aren't. **FastContext** (Microsoft Research, published 12 June 2026 —
days old at the time of writing) is a trained explorer model that finds relevant
code and hands back file:line citations, so the main agent never burns its own
context grepping. Only the 4B explorers are
released (SFT and RL variants on Hugging Face); serve the **RL** one. **context-mode** (mksglu) is
generic middleware that stops *any* large tool output from entering the
conversation at all, indexing it and serving back only the slice you ask for.
FastContext attacks the *exploration* leg; context-mode attacks *every other*
leg. They are complementary and run happily side by side.

There is no official FastContext integration for Claude Code or Codex — it ships
wired to Mini-SWE-Agent. A third-party MCP server,
[`Jakevin/fastcontext-agent-tools`](https://github.com/Jakevin/fastcontext-agent-tools),
bridges that gap. Its code is small and its security posture is sound (resolved
path allowlisting, read-only, citation validation), but it vendors a snapshot of
Microsoft's code, hand-rolls the MCP protocol, and is an early single-author
project. Recommendation: usable today if you pin to a reviewed commit; a modest
fork could make it considerably better. Details and a proposed fork plan below.

---

## The two approaches

Both tools exist because LLM coding agents waste a large fraction of their token
budget on exploration and tool noise — reading files to find the one relevant
function, dumping a 7 MB JSON to extract one record, scrolling a git log. The
two tools cut that waste at opposite ends of the pipeline.

### FastContext — a trained explorer subagent

- **Source:** Microsoft Research, arXiv:2606.14066 (submitted 12 Jun 2026;
  **withdrawn 30 Jun 2026**), code at `github.com/microsoft/fastcontext`.
- **Idea:** Separate *exploration* from *solving*. Most agents use one model for
  both, so every exploratory read and search pollutes the solver's history.
  Microsoft's own measurement makes the size of the problem concrete: in GPT-5.4
  trajectories, reading and searching account for **56.2% of all tool-use turns**
  and **46.5% of the main agent's total tokens**. FastContext is a dedicated
  subagent, invoked on demand, that issues parallel read-only tool calls
  (`READ`, `GLOB`, `GREP`) and returns compact file paths and line ranges as
  focused context.
- **Mechanism:** Specialised exploration models (4B–30B parameters) bootstrapped
  from strong reference-model trajectories via SFT, then refined with
  task-grounded RL. Detail in *The model family* below.
- **What it costs you:** You serve the model. The compression comes from a small
  expert doing the searching, off the solver's context. It is domain-specific:
  it explores code repositories, nothing else.

#### The model family: SFT, RL, and what to serve

Only the **4B** explorers are published on Hugging Face today —
`microsoft/FastContext-1.0-4B-SFT` and `microsoft/FastContext-1.0-4B-RL`, both
updated within the last day. The **30B** model is a scaling reference in the
paper, not (yet) a release; the public collection contains the two 4B models
only.

- **Backbones:** Qwen3-4B-Instruct (4B explorer); Qwen3-Coder-30B-A3B (30B
  scaling reference).
- **Context length:** up to 262K tokens.
- **Tools exposed to the model:** exactly three, all read-only — `READ`
  (line-numbered file contents), `GLOB` (path discovery by pattern), `GREP`
  (ripgrep-style regex search).
- **Exploration loop:** query understanding → parallel tool calls (several
  `READ`/`GLOB`/`GREP` in one turn) → observation-driven refinement → a compact
  `<final_answer>` citation block.

**SFT vs RL — the distinction that matters for deployment.** FastContext is
trained in two stages, and each stage is shipped as a separate model:

- **`FC-4B-SFT` (supervised fine-tuning).** Qwen3-4B-Instruct trained by
  *imitation* on curated exploration traces from a stronger reference model. The
  traces are split into three sources that match the subagent's runtime
  behaviour: `parallel_toolcalls` (broad first-turn search), `multiturn_traj`
  (multi-turn evidence gathering), and `linerange` (precise citation
  generation). It learns what good exploration looks like by copying it.
- **`FC-4B-RL` (reinforcement learning).** Takes the SFT model and refines it
  *on-policy*: it is rolled out as the actual subagent and optimised with
  **GRPO** against a deterministic reward — file- and line-level **F1** (citation
  accuracy), a bonus for bounded parallel exploration (efficiency), and format
  penalties. It learns from its own outcomes rather than from imitation alone.

In short: SFT teaches the behaviour offline by example; RL sharpens it online
against a reward for accurate, efficient citations.

**Which to serve: prefer `FC-4B-RL`.** Microsoft lists both 4B models as
deployment targets, but RL wins on their own numbers — higher accuracy and
larger token cuts — and the compact 4B-RL can even match or beat the 30B-SFT
scaling reference (e.g. GLM-5.1 on SWE-bench Pro, 22.5 vs 20.0 with fewer
resources). The MCP server's README defaults `MODEL` to `-4B-SFT`; switching it
to `-4B-RL` is the cheap win.

#### Evaluation (Mini-SWE-Agent)

Each cell is **resolution score / main-agent tokens**; deltas are relative to the
same main agent run with no explorer (`none`). Three main agents were tested —
GPT-5.4, GLM-5.1, Kimi-K2.6 — against the unreleased 30B-SFT scaling reference
and the two released 4B models.

| Main agent | Subagent | SWE-bench Multilingual | SWE-bench Pro | SWE-QA |
|---|---|---|---|---|
| **GPT-5.4** | none | 71.7 / 457k | 46.0 / 818k | 81.3 / 418k |
| | FC-30B-SFT | 75.0 (↑3.3) / 356k (↓22.1%) | 49.0 (↑3.0) / 688k (↓15.9%) | 82.0 (↑0.7) / 206k (↓50.7%) |
| | FC-4B-SFT | 73.3 (↑1.6) / 364k (↓20.4%) | 47.0 (↑1.0) / 689k (↓15.8%) | 81.9 (↑0.6) / 213k (↓49.0%) |
| | FC-4B-RL | 74.7 (↑3.0) / 338k (↓26.0%) | 48.5 (↑2.5) / 701k (↓14.3%) | 82.0 (↑0.7) / 210k (↓49.8%) |
| **GLM-5.1** | none | 72.3 / 2514k | 17.5 / 2692k | 72.7 / 401k |
| | FC-30B-SFT | 73.7 (↑1.4) / 1797k (↓28.5%) | 20.0 (↑2.5) / 2370k (↓12.0%) | 73.3 (↑0.6) / 292k (↓27.2%) |
| | FC-4B-SFT | 73.3 (↑1.0) / 1919k (↓23.7%) | 18.0 (↑0.5) / 2279k (↓15.3%) | 73.4 (↑0.7) / 306k (↓23.7%) |
| | FC-4B-RL | 73.7 (↑1.4) / 1971k (↓21.6%) | **22.5 (↑5.0)** / 2210k (↓17.9%) | 73.5 (↑0.8) / 302k (↓24.7%) |
| **Kimi-K2.6** | none | 76.3 / 1553k | 31.0 / 2383k | 71.6 / 510k |
| | FC-30B-SFT | 76.7 (↑0.4) / 1360k (↓12.4%) | 33.0 (↑2.0) / 2150k (↓9.8%) | 72.8 (↑1.2) / 373k (↓26.9%) |
| | FC-4B-SFT | 75.3 (↓1.0) / 1306k (↓15.9%) | 32.5 (↑1.5) / 2159k (↓9.4%) | 72.6 (↑1.0) / 402k (↓21.2%) |
| | FC-4B-RL | **78.3 (↑2.0)** / 1384k (↓10.9%) | 33.5 (↑2.5) / 2158k (↓9.4%) | 72.6 (↑1.0) / 378k (↓25.9%) |

What the table actually shows: accuracy improves in nearly every cell (one
regression, Kimi 4B-SFT on Multilingual), token cuts run 9–51%, and **4B-RL beats
4B-SFT in most cells** — most strikingly Kimi Multilingual (78.3 vs 75.3) and GLM
SWE-bench Pro (22.5 vs 18.0, where 4B-RL also beats the 30B-SFT's 20.0). The
single largest token cut here is GPT-5.4 on SWE-QA (~51% with 30B-SFT).

*Caveat on the headline numbers.* The abstract/model-card claim "up to 5.5 points
and up to ~60% tokens." Those upper bounds do not appear in this Mini-SWE-Agent
table (its maxima are +5.0 accuracy and ~51% tokens); they likely come from other
configurations in the full paper. Treat the table cells as the verifiable
figures.

#### Standalone exploration quality (the clearest SFT-vs-RL signal)

Measured as citation F1 against patch-derived locations, on the 4B explorer:

| Stage | File-level F1 | Module-level F1 | Function-level F1 |
|---|---|---|---|
| base (Qwen3-4B) | 62.57 | 51.25 | — |
| + SFT | 70.55 | 55.26 | — |
| + RL | 71.48 | 56.26 | 38.45 |

The big jump is **SFT** (imitation lifts file-F1 ~8 points); **RL** adds a smaller
gain that comes mainly from higher recall at similar precision — consistent with
a reward that rewards covering patch-relevant locations. This matters for the
"should we train" question below: most of the available gain lives in the cheap
SFT stage, not the expensive RL stage.

### context-mode — a generic output sandbox

- **Source:** `github.com/mksglu/context-mode`, an npm package and Claude Code
  plugin. Tagline: "the other half of the context problem."
- **Idea:** Never let raw bytes into the conversation. Tool output (bash, fetch,
  file reads, JSON, git history) is executed in a sandbox, indexed into an FTS5
  store, and only the derived answer or a matched snippet is returned to the
  model.
- **Mechanism:** Deterministic plumbing — an MCP server plus hooks and slash
  commands, integrating across ~15 agent platforms. No model required; it leans
  on the *main* agent's intelligence to query the index.
- **Reported gains:** Task-specific, but large on output-heavy work — its own
  examples cite 94–99% context reduction (e.g. a 7.5 MB JSON reduced to ~0.9 KB
  of conversation).
- **What it costs you:** Almost nothing to run; it is plumbing. It is
  domain-agnostic, which is its strength and its limit — it doesn't make
  exploration *smarter*, it just stops output from flooding context.

### Why they are complementary, not competing

| | FastContext | context-mode |
|---|---|---|
| Layer | Upstream: *finding* the code | Downstream: *handling* tool output |
| Mechanism | Trained model returns citations | Sandbox + index returns slices |
| Domain | Code repositories only | Any large tool output |
| Needs a model? | Yes (4B self-served; 30B is a paper reference) | No |
| Compression from | Expert exploration off-context | Bytes never enter context |
| Proven gains | up to +5.0 pts, −9–51% tokens per cell (Mini-SWE-Agent; abstract claims up to +5.5 / ~60%) | ~94–99% on output-heavy tasks |
| Integration | Built for Mini-SWE-Agent | MCP + hooks, ~15 platforms |

FastContext answers *"where is the relevant code?"* cheaply. context-mode ensures
that when you then run tests, fetch docs, or read a large file, none of that
floods the context either. If you already run context-mode (this note was
researched with it), adding FastContext as an MCP explorer is additive.

---

## The MCP bridge: `Jakevin/fastcontext-agent-tools`

FastContext as published does not plug into Claude Code or Codex — it is wired to
Mini-SWE-Agent through prompt YAMLs. This third-party project supplies the
missing bridge: a stdio MCP server (`fastcontext_mcp`) and a Codex skill
(`fastcontext-explorer`). It is **not** affiliated with Microsoft. Version 0.2.1,
MIT licence, single author, ~25 commits, with a `tests/` directory, a CI
workflow, and setup docs in English, Traditional Chinese, and Japanese.

It does not bundle weights or run inference. You serve a FastContext model on an
OpenAI-compatible endpoint; the server shells out to the bundled CLI and returns
citations for your main agent to verify.

### Architecture, as read from the source

- **Entry point** (`__main__.py`) is a one-liner into `server.main()`.
- **`server.py`** hand-rolls the MCP JSON-RPC protocol (`PROTOCOL_VERSION =
  "2024-11-05"`) — no official `mcp` SDK. It builds `text_result` dicts manually
  and routes `initialize` / tool calls itself.
- **`runtime.py`** holds the real logic: path resolution, the subprocess call,
  citation parsing and validation, and a `health()` probe.
- **One tool, `fastcontext_explore`:**
  ```json
  {
    "repo_path": "/path/to/repo",
    "query": "Locate the request validation logic for uploaded files",
    "max_turns": 6,
    "citation": true,
    "timeout_seconds": 300
  }
  ```
  It returns `{ ok, returncode, repo_path, query, citations, citation_warnings,
  raw_output, stderr, trajectory_path }`.
- **Configuration** is environment-only:
  ```
  BASE_URL="http://127.0.0.1:30000/v1"        # SGLang default port; vLLM also fine
  MODEL="microsoft/FastContext-1.0-4B-SFT"     # prefer -4B-RL (see model family above)
  API_KEY="..."                                # when the endpoint requires auth
  FASTCONTEXT_ALLOWED_ROOTS="/path/to/repos"   # os.pathsep-separated allowlist
  ```

### Security review (verified in code, not just the README)

The posture is better than the README alone implies:

- **Path traversal is properly closed.** `resolve_repo_path()` runs
  `Path(repo_path).expanduser().resolve()` — collapsing `..` and resolving
  symlinks — *before* the containment check
  (`repo == root or root in repo.parents`). You cannot escape
  `FASTCONTEXT_ALLOWED_ROOTS` with `../../etc` or a symlink. This is the check
  most naive wrappers get wrong; this one is correct.
- **Genuinely read-only.** Only `fastcontext_explore` is exposed — no edit/write
  tool. FastContext's own tools are read-only (`READ`/`GLOB`/`GREP`). The server
  never reads file *contents* back into your agent; it returns citations for the
  main agent to open.
- **Citations are validated.** `validate_citations(repo, …)` checks returned
  paths against the repo and emits `citation_warnings`, so a hallucinated path is
  flagged rather than trusted.
- **No shell injection surface.** The CLI is invoked as a module
  (`[sys.executable, "-m", "fastcontext_mcp.fastcontext_cli"]`), and the user
  query is injected into the *model prompt*, not a shell string. Secrets come
  from env vars only. A `timeout_seconds` guard (default 300) bounds runaway
  exploration.

### Concerns

1. **"Pinned dependency" vs vendored.** The README says it installs Microsoft
   FastContext "from the pinned official source revision," but the code imports
   `fastcontext_mcp.fastcontext_cli` — the CLI lives inside *this package's*
   namespace. FastContext isn't on PyPI, so this is almost certainly a vendored
   copy (or a git-URL pin). You are trusting this author's snapshot of
   Microsoft's code, and upstream fixes won't reach you until they re-vendor.
   Confirm the revision before relying on it long-term.
2. **Hand-rolled MCP on an older protocol.** Simple and readable, but it won't
   track protocol changes automatically, and edge cases (cancellation, progress,
   partial results) are the author's to maintain.
3. **Early, single-author, low adoption.** v0.2.x. Pin to a commit you've read;
   the runtime logic is ~8 KB and reviewable end to end.
4. **The real prerequisite is the model.** You must serve
   `microsoft/FastContext-1.0-4B-SFT` (or a larger variant) yourself. Each
   `fastcontext_explore` call is a multi-turn agent loop (up to `max_turns`), so
   it has real wall-clock cost — use it for "where is X" questions, not for
   things a single grep would answer.

### Verdict

Sound for what it is, and worth adopting over hand-rolling the wrapper, with two
guardrails: **pin to a reviewed commit** (not `main`, and confirm the vendored
FastContext revision), and **set `FASTCONTEXT_ALLOWED_ROOTS` explicitly** rather
than relying on the launch-directory default.

---

## Proposed fork and improvements

The project is a good base. A fork could close the maturity gaps and add real
ergonomic and performance wins. Roughly in priority order:

### Correctness and trust

1. **Make the FastContext source explicit and verifiable.** Either a proper
   git-URL dependency pinned to a SHA in `pyproject.toml`, or a vendored copy
   with the upstream commit recorded in-tree. Surface that SHA in `health()` so
   operators know exactly which Microsoft snapshot they're running. Add a CI job
   that diffs the vendored module against upstream and fails on drift.
2. **Harden the allowlist default.** Refuse to start (or log loudly) when
   `FASTCONTEXT_ALLOWED_ROOTS` is unset, instead of silently defaulting to the
   launch directory. Fail closed.
3. **Strengthen citation handling.** Optionally drop or attempt to correct
   invalid citations rather than only warning; bounds-check line ranges against
   actual file length; de-duplicate overlapping ranges.
4. **Tests for the security-critical paths.** Explicit cases for `..` traversal,
   symlink escape, allowlist boundaries, and citation-parser edge cases
   (back-ticked lines, ranges, missing `<final_answer>`).

### Protocol and ergonomics

5. **Adopt the official MCP Python SDK.** Replaces the hand-rolled JSON-RPC,
   tracks newer protocol versions, and unlocks cancellation and progress
   notifications — which matter because exploration is slow.
6. **Emit progress during exploration.** Stream per-turn progress as MCP
   notifications so the calling agent (and the user) sees the explorer working
   rather than a 5-minute silence.
7. **Ship a `uvx`/`pipx` install and a Claude Code plugin.** A one-line
   `uvx fastcontext-mcp` lowers the barrier; a plugin package (slash command or
   subagent plus a CLAUDE.md nudge to prefer `fastcontext_explore` over manual
   grep) mirrors how context-mode drives adoption.

### Performance

8. **Cache results.** Key on (repo content hash or git HEAD + normalised query)
   → citations, invalidated on HEAD change. Exploration is expensive and queries
   repeat across a session.
9. **Allow concurrency.** A bounded worker pool for parallel `explore` calls
   instead of one subprocess at a time, with a configurable cap.
10. **Tiered model routing.** Route simple "where is X" queries to the 4B model
    and harder multi-hop queries to a larger variant, by heuristic or an explicit
    parameter, to balance latency against recall.

### Measurement

11. **Report explorer cost.** Return tokens consumed and wall-clock per call so
    users can measure the 60% main-agent saving in their own setup rather than
    taking the paper's number on faith.

### Optional, behind a flag

12. **Return bounded snippets.** Off by default. When enabled, include N lines
    around each citation so the main agent skips a round of file reads. This
    trades the read-only-citations purity (and some token savings) for fewer
    round trips; keep it opt-in so the default behaviour preserves context.

### Suggested first cut

If forking, the highest value-for-effort slice is **(1) explicit pinned source +
SHA in health**, **(2) fail-closed allowlist**, **(5) official MCP SDK**, and
**(8) result caching**. That addresses the trust gap, the one safety default
worth changing, the protocol-maintenance risk, and the biggest latency
complaint — without touching the model side at all.

---

## Could we train our own explorer? What, how, and whether it's worth it

The model card and paper describe a concrete, surprisingly small training recipe,
and the code and data are released, so "train our own" is feasible. But the
answer is not one-size-fits-all — it depends on the codebase and the scale you're
deploying at. The single-repo intuition ("don't bother") is right for a small
project and wrong for an org platform. Below is the recipe, then a decision
framework that spans this project *and* the more general cases (a C# or Python
API backend, a polyglot monorepo, a fleet of services).

### When training is worth it — the three variables

The decision turns on three things, not on "is it my repo":

1. **Language/framework coverage in the base model.** The 4B explorer is built on
   Qwen3-4B-Instruct and trained on SWE-bench-style tasks, which skew toward
   Python, JS/TS, Java, Go, Rust, C++ (SWE-bench Multilingual). Practical read:
   **Python backends (FastAPI/Django/Flask) and TS frontends are well-covered**
   off the shelf; **C#/.NET is thinner**, so an ASP.NET Core API is the most
   likely single-language case to benefit from adaptation — its conventions
   (`.csproj`, DI registration in `Program.cs`, attributes, EF Core migrations,
   partial classes) are exactly the kind of structural priors a model learns from
   exposure.
2. **Repo size and indirection.** A small single-purpose repo is easy to explore
   with stock GLOB/GREP. A large or polyglot monorepo (C# backend + TS frontend +
   IaC) has more cross-language hops and config indirection, where a tuned
   explorer — or at least strong context injection — pays off more.
3. **How many repos and developers you're serving.** This is the variable that
   flips the economics. Training for *one* repo rarely repays the effort. Training
   once for a *platform team* spanning dozens of services amortises across every
   repo and every developer, and a domain-adapted explorer becomes a sensible
   shared asset.

### How Microsoft trained it (so we know what we'd be copying)

- **Stage 1 — SFT (imitation), ~3k examples.** 2,954 filtered examples generated
  by having a strong reference model (**Sonnet 4.6**) explore SWE-bench-style
  tasks with the same `READ`/`GLOB`/`GREP` tools used at inference. Split three
  ways to match runtime behaviour: `parallel_toolcalls` (990, broad first turn),
  `multiturn_traj` (983, full trajectories), `linerange` (981, final
  `<final_answer>` citations). Each task's top-level directory listing is baked
  into the system prompt. This stage does the heavy lifting (file-F1 62.6 → 70.6).
- **Stage 2 — RL (GRPO), 400 prompts over 395 repos.** Initialised from the SFT
  checkpoint. Crucially, **labels are derived automatically from reference
  patches**: parse the patch, convert each hunk into a target file + line range
  (avg ~11 ranges/prompt). The model is rolled out as the real subagent (up to 8
  turns, served on SGLang, 16 trajectories/prompt, 1,000 steps) and rewarded by a
  deterministic function = file-F1 + line-F1 + a small bounded-parallelism bonus
  − format penalties (empty/over-long/malformed/excessive-fan-out). RL adds
  recall (file-F1 → 71.5, and unlocks function-level citation).

The key insight for us: **the RL labels are free if you have a patch.** A
bug-fix commit's changed files and line ranges *are* the ground-truth "relevant
locations" for the issue that motivated it. We have a deep git history — that is a
ready-made label source.

### What we'd actually train, in three tiers

1. **Tier 0 — don't train (default for almost everyone).** Serve the released
   `4B-RL` and invest in *prompt-level* levers instead: inject the repo's
   top-level layout into the explorer system prompt (Microsoft does exactly
   this), and write a sharp CLAUDE.md / AGENTS.md nudge for when to call the
   explorer (detailed in the next subsection). This is the right call for this
   game repo, for any well-covered single stack (a FastAPI or Django service, a
   TS frontend), and as the *first* move even when you later decide to train.
2. **Tier 1 — light SFT domain-adaptation (when a measured gap exists).** Do a
   small LoRA SFT pass on the `4B-SFT` or `4B-RL` checkpoint when a held-out eval
   shows the stock model missing your conventions. Likeliest beneficiaries: a
   **C#/.NET API** (citations that miss DI wiring in `Program.cs`, EF migrations,
   or attribute-routed controllers), a large **polyglot monorepo** (cross-language
   localisation), or this repo's own quirks (the worker/engine split, CSS-Modules,
   the `data/scenarios` ↔ `public/data` indirection).
   - **Data:** take real "where is X" questions (dev history, issue trackers, or
     generated from recent commits), have a strong reference model (Sonnet)
     explore the repo with Read/Glob/Grep, keep the successful traces, and
     serialise into the same three splits. A few hundred examples is enough to
     start — the original corpus was only ~3k.
   - **Effect:** better recall/precision on your idioms and naming. Bounded; only
     pursue once the eval set (below) confirms a gap.
3. **Tier 2 — full RL with a task-grounded reward (platform/research scale).**
   Replicate the GRPO stage with labels mined automatically from git history
   (changed files/lines per fix commit across many repos), or a custom reward —
   e.g. reward citations the main agent actually opened, or that overlapped the
   eventual fix. Needs GPUs, a served rollout endpoint, and a reward pipeline.
   Worth it when you're building a *shared explorer for a fleet of services* or
   doing research — not for any single application repo, in any language.

### To what effect — be realistic

- The standalone-F1 numbers say the **SFT stage captures most of the gain**; RL is
  a recall top-up. So Tier 1 (light SFT) is the sweet spot *if* you train, and
  Tier 2's extra cost buys comparatively little except at fleet scale.
- **Build the eval set first, regardless of tier or language.** Assemble 30–50
  "where is X" questions for the target repo with known answer locations (mine
  them from fix commits — `git log -p` gives you the changed files/lines for
  free). Measure the released `4B-RL` against it. If it scores well — likely for
  Python/TS — the training question is answered: don't. If it lags (watch the
  C#/.NET case), that same eval set tells you whether Tier 1 helped.
- A non-training alternative often beats light training: **distil the repo's
  structure into the explorer's context** (directory listing, a short
  architecture note, key entry points, framework conventions) — cheap, immediate,
  no GPUs, and it works across languages.

**Bottom line:** the recipe is small enough to reproduce and git history hands you
free labels, but the rational order is the same everywhere — *use 4B-RL → measure
on a homemade eval set → inject repo structure via the prompt → only then, and
only if the eval shows a gap, consider a light SFT pass*. For a single app repo
(this one, or a Python/TS service) stop at the prompt level; reserve full RL for a
platform team standing up a shared explorer across many services.

### Prompt-level levers: the CLAUDE.md / AGENTS.md nudge

This is the cheapest, highest-leverage lever, and it is what makes the difference
between an explorer that gets used well and one that sits idle or gets
over-called. A trained model only helps if the *main* agent invokes it at the
right moments. The nudge is a short block in the agent's instructions file
(`CLAUDE.md` for Claude Code, `AGENTS.md` for Codex; the bundled
`fastcontext-explorer` skill already encodes part of this for Codex) that does
three jobs:

1. **Trigger** — name the situations where delegating beats self-exploration.
2. **Anti-trigger** — name the situations where calling it just adds latency.
3. **Post-call discipline** — tell the agent what to do with the citations so it
   doesn't undo the saving.

The paper's own runtime prompt (Appendix B) is the template: use the explorer for
cold-start exploration, broad cross-file localisation, or *after* a direct search
fails; skip it when the issue already names the file or symbol; and after a call,
open only the returned narrow line ranges and do **not** repeat a repo-wide search
for the same thing. That last clause is the one people forget — without it the
agent greps anyway and you pay twice.

**Why calibration matters.** Each `fastcontext_explore` call is a multi-turn agent
loop (up to 8 turns), so it has real latency. Too eager a nudge and the agent
delegates trivially-greppable lookups; too timid and it never delegates the broad
searches that actually pollute context. Tune the trigger wording, and pair it with
**structure injection** — a few lines of repo layout in the prompt — which lifts
exploration quality with zero training.

#### A generic nudge (drop-in starting point)

```markdown
## Repository exploration

For "where/how is X implemented", broad cross-file localisation, or after a
direct grep/glob fails, call the `fastcontext_explore` MCP tool with a
natural-language query and the repo path — do NOT hand-grep the whole tree first.

Skip it when the relevant file or symbol is already named, or for a one-line
lookup you can resolve with a single grep.

After a call: open only the cited line ranges with narrow windows. Do not re-run
broad repository-wide searches for information the explorer already returned.
Treat citations as candidates — verify before editing.
```

#### Tailor the trigger and seed structure per project

The generic block works; it works *better* with a few repo-specific lines that
tell the explorer (and the main agent) the shape of the codebase. Examples:

- **This repo (TS / Preact / PixiJS):**
  ```markdown
  Architecture: engine (`src/engine/`, runs in a WebWorker, pure logic) ↔ UI
  (`src/ui/`, Preact + signals) ↔ renderer (`src/renderer/`, PixiJS). Worker
  protocol in `src/engine/protocol.ts`. Scenario data: `data/scenarios/` (source)
  → `public/data/` (served). When localising a feature, expect logic in
  `src/engine/` and its wiring in a panel under `src/ui/panels/`.
  ```
- **C# / ASP.NET Core API:**
  ```markdown
  Layers: Controllers → Services → Repositories → EF Core DbContext. DI is
  registered in `Program.cs`/`Startup.cs`; config in `appsettings*.json`. Routes
  are attribute-based (`[Route]`/`[HttpGet]`). For "where is endpoint X handled",
  explore the controller, then the injected service, then the EF entity/migration.
  Prefer `*.cs` source over generated `obj/` output.
  ```
- **Python / FastAPI (or Django):**
  ```markdown
  FastAPI: routers under `app/api/`, dependencies via `Depends(...)`, models in
  `app/models/` (Pydantic) and `app/db/` (SQLAlchemy), migrations in `alembic/`.
  (Django: URLs in `urls.py` → views → models; migrations in `*/migrations/`.)
  For "where is endpoint X", trace router → dependency → service → model.
  ```

Two cross-cutting tips for any project: put the framework-convention hints where
the explorer system prompt can see them (not just the main agent's CLAUDE.md), and
for a polyglot monorepo state the language boundaries explicitly ("API in
`/backend` is C#; web in `/frontend` is TS") so the explorer doesn't waste turns
crossing them blindly. None of this requires training — it is the Tier-0 win that
usually closes most of the gap a light SFT pass would have chased.

---

## Standing it up (either as-is or forked)

1. Serve the model on an OpenAI-compatible endpoint (default config expects port
   30000). Prefer the RL variant. The model card's SGLang invocation:
   ```bash
   python3 -m sglang.launch_server \
       --model-path FastContext-1.0-4B-RL \
       --tool-call-parser qwen \
       --context-length 262144 \
       --trust-remote-code \
       --dtype bfloat16 \
       --host 0.0.0.0 --port 30000 \
       --tp-size 1 --mem-fraction-static 0.8
   ```
2. Install the package (`pip install -e .`), which pulls in the bundled
   FastContext CLI.
3. Register the MCP server. For Claude Code, the README's `mcpServers` JSON block
   is correct; set `BASE_URL`, `MODEL`, `API_KEY`, and `FASTCONTEXT_ALLOWED_ROOTS`.
   For Codex, symlink the `fastcontext-explorer` skill into `~/.codex/skills`.
4. Add the nudge to `CLAUDE.md` (or `AGENTS.md` for Codex) so the agent calls
   `fastcontext_explore` at the right times — see *Prompt-level levers* above for
   a drop-in block and per-language variants. Seed repo structure while you're
   there; it's the cheapest quality win.

It runs alongside context-mode without conflict: FastContext trims the
exploration leg, context-mode trims every other tool's output.

## Sources

- FastContext paper — arXiv:2606.14066
- `github.com/microsoft/fastcontext`
- Model card — `huggingface.co/microsoft/FastContext-1.0-4B-SFT`
- Collection — `huggingface.co/collections/microsoft/swe-fastcontext`
  (`FastContext-1.0-4B-SFT`, `FastContext-1.0-4B-RL`)
- `github.com/mksglu/context-mode`
- `github.com/Jakevin/fastcontext-agent-tools` (source read: `server.py`,
  `runtime.py`, `__main__.py`, `pyproject.toml`, README)
