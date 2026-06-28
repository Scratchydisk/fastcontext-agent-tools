# Running FastContext-agent-tools locally

How to stand up this MCP server on a workstation with a GPU, unchanged.
Companion to [fastcontext-vs-context-mode.md](fastcontext-vs-context-mode.md).

## The shape of it

Two independent processes:

1. **Model server** (`scripts/serve-model.sh`) — vLLM serving the FastContext
   model on an OpenAI-compatible endpoint at `http://127.0.0.1:30000/v1`.
   Long-running, uses the GPU.
2. **MCP server** (`python -m fastcontext_mcp`) — *not* a daemon; the agent
   client (Claude Code / Codex) spawns it over stdio. It shells out to the
   bundled `fastcontext.cli`, which calls the model server and returns file:line
   citations.

The MCP layer is lightweight (openai/httpx/pydantic — no torch). All GPU weight
is in the model server, kept in a separate venv (`.venv-serve`).

**Where files are read:** the `READ`/`GLOB`/`GREP` tools run inside the
`fastcontext.cli` process (the MCP box), not on the model server. The model
server only does inference. So the repo being explored must live on the machine
running the MCP, and `FASTCONTEXT_ALLOWED_ROOTS` is always local.

## Scripts

| File | Purpose |
|---|---|
| `scripts/env.sh` | Committable defaults for the 4 env vars the MCP reads; sources `env.local.sh` last. |
| `scripts/env.local.sh` | **Gitignored.** Per-machine values: `FASTCONTEXT_ALLOWED_ROOTS`, `HF_TOKEN`, remote endpoint, small-GPU flags. Copy from `env.local.sh.example`. |
| `scripts/env.local.sh.example` | Committed template for the above, incl. the verified small-GPU recipe (commented out). |
| `scripts/kickoff.sh` | Install if needed → `--print-health` → optional live `explore` smoke test. |
| `scripts/serve-model.sh` | Launch vLLM for the model. Run in its own terminal. |

All paths are derived from the script location, so the repo can live anywhere.

## Checkpoint A — MCP works unchanged (no model needed)

```bash
./scripts/kickoff.sh          # creates .venv (py3.12), installs, prints health
```
Expect `"ok": true`, the bundled FastContext importing, and the test suite
passing (`python -m unittest tests.test_server` → 18/18).

## Checkpoint B — live exploration (needs the model)

```bash
# terminal 1 — serve the model (first run downloads ~8 GB weights + vLLM)
export HF_TOKEN=hf_...                 # or set it in scripts/env.local.sh
./scripts/serve-model.sh
# wait for the Uvicorn "Application startup complete" line on :30000

# terminal 2 — fire a real explore against this repo
./scripts/kickoff.sh explore
```

### Notes / gotchas

- **Tool calling is mandatory.** `fastcontext/agent/llm.py` reads server-side
  `tool_calls`. vLLM must run with `--enable-auto-tool-choice --tool-call-parser
  hermes` (already in `serve-model.sh`). If `explore` returns no citations, the
  parser is the first suspect — try `qwen3_xml`.
- **Lower `FC_TEMPERATURE` for accuracy.** FastContext defaults to 0.7, which is
  high for a deterministic locate task and causes occasional wrong or missed
  citations. Setting `FC_TEMPERATURE=0.2` raised the accuracy benchmark from 80%
  to 93% (12/15 to 14/15 over three iterations) and made the search more
  deterministic. See [benchmarks/](../benchmarks/).
- **Blackwell (RTX 5090, sm_120).** Verified with vLLM 0.23.0 + torch 2.11+cu130
  against driver/CUDA 13.x. The server resolves `Qwen3ForCausalLM` and loads
  with FlashAttention 2 / FlashInfer.
- **First-boot weight download.** Without `HF_TOKEN` the unauthenticated HF Hub
  pull can rate-limit/stall; set a token to make it reliable.
- **Context length** defaults to 65536 (`CTX_LEN` env to override); the model
  supports up to 262144. That default assumes a ~24 GB card — on smaller cards
  vLLM will refuse to start ("estimated maximum model length is N"). See
  [Context length by VRAM](#context-length-by-vram) for what fits.
- **ripgrep is required.** The `GREP`/`GLOB` tools shell out to `rg`. If it's
  not on `PATH`, searches fail with "No such file or directory: 'rg'", the agent
  reads nothing, and `explore` returns no/garbage citations. Install it
  (`apt install ripgrep`, or a static binary on `PATH`). When the MCP is spawned
  by Claude Code, make sure its `env.PATH` includes wherever `rg` lives.

## Small GPUs (≈8 GB) — quantised serving

FastContext-4B is ~8 GB of BF16 weights, so it will **not** fit on an 8 GB card
at full precision (it OOMs while loading weights). It can still run via 4-bit
quantisation plus a few headroom/quality flags. All of them are opt-in env vars
with safe defaults, so larger GPUs are unaffected — copy the template and
uncomment the small-GPU block:

```bash
cp scripts/env.local.sh.example scripts/env.local.sh
# then uncomment the "Small-GPU recipe" block
```

What the block sets, and why (verified on an RTX A2000 8 GB):

| Var | Value | Why |
|---|---|---|
| `QUANT` | `bitsandbytes` | 4-bit weights (~2.5 GB); BF16 won't fit. |
| `CTX_LEN` | `16384` | Small KV cache (only ~0.8 GB free at this size). |
| `GPU_MEM_UTIL` | `0.85` | Leave room for the CUDA context. |
| `ENFORCE_EAGER` | `1` | Skip CUDA-graph capture (else OOM after weights load). |
| `VLLM_USE_FLASHINFER_SAMPLER` | `0` | flashinfer sampler may not JIT-compile; use native. |
| `FC_MAX_TOKENS` | `4000` | Cap output tokens so prompt+output stays under `CTX_LEN` with room to read files (native FastContext env var, default 4096). |
| `FASTCONTEXT_REROOT_PATHS` | `1` | Re-root truncated citation/tool paths back under the workspace. Worth keeping on at any precision (see note below); quantisation just makes the truncation more frequent. |

The serving flags (`QUANT`, `ENFORCE_EAGER`, `GPU_MEM_UTIL`, `CTX_LEN`) come at a
quality or latency cost, so leave them unset on a larger card. `FASTCONTEXT_REROOT_PATHS`
is the exception: a benchmark on a full-precision 12 GB endpoint still saw the
model truncate paths in some citations, and turning re-rooting on raised the
file-hit rate from 3/5 to 5/5. Keep it on regardless of GPU; it leaves
already-correct paths untouched.

## Context length by VRAM

The default `CTX_LEN=65536` only fits on a ~24 GB card. BF16 weights are a fixed
~8 GB; the rest of VRAM becomes KV cache, and the KV cache for this model costs
roughly ~140 KB per token — so `max_model_len` scales with whatever's left after
the weights. If you ask for more than fits, vLLM refuses to start and prints the
estimated maximum (e.g. *"estimated maximum model length is 20080"*) rather than
OOM-ing mid-run.

| VRAM | Precision | Suggested `CTX_LEN` | Extra env |
|---|---|---|---|
| ~8 GB | 4-bit (`QUANT=bitsandbytes`) | `16384` | the full small-GPU block above |
| ~12 GB | full BF16 | `16384` (safe) … `24576` (push) | `GPU_MEM_UTIL=0.95` for the upper end |
| ~16 GB | full BF16 | `32768` | — |
| ≥24 GB | full BF16 | `65536` (default), up toward `262144` | — |

Rules of thumb:
- Keep `FC_MAX_TOKENS` (default 4096) well below `CTX_LEN` — the agent's prompt
  grows as it reads files, and `prompt + output` must stay under `CTX_LEN`.
- Hitting the ceiling? Lower `CTX_LEN` first; raising `GPU_MEM_UTIL` (toward 0.95)
  buys only a little more KV cache since the weights are fixed.
- Prefer lowering `CTX_LEN` over enabling `QUANT` on a 12 GB+ card. 4-bit frees
  memory but degrades quality.

## Registering with Claude Code (after Checkpoint B works)

Point the MCP client at the MCP venv's Python so it imports the right install
(adjust the absolute path to your checkout):

```json
{
  "mcpServers": {
    "fastcontext": {
      "command": "/abs/path/to/fastcontext-agent-tools/.venv/bin/python",
      "args": ["-m", "fastcontext_mcp"],
      "env": {
        "BASE_URL": "http://127.0.0.1:30000/v1",
        "MODEL": "microsoft/FastContext-1.0-4B-RL",
        "API_KEY": "local-no-auth",
        "FASTCONTEXT_ALLOWED_ROOTS": "/abs/path/to/your/repos"
      }
    }
  }
}
```

**The MCP client does not source `env.local.sh`.** Only the shell scripts
(`kickoff.sh`, `serve-model.sh`) read it. When Claude Code spawns the MCP
server it passes only the `env` block above — so any var your setup relies on
(`FC_MAX_TOKENS`, `FASTCONTEXT_REROOT_PATHS`, a `PATH` that finds `rg`,
`FASTCONTEXT_ALLOWED_ROOTS`) must be duplicated here too. Editing the block
doesn't reach an already-running server; reconnect (restart Claude Code) after
changes. `FASTCONTEXT_ALLOWED_ROOTS` may be `/` to allow exploring any path.

For serving the model on a separate machine, see the **Hosting the model on a
remote server** section in the [README](../README.md).
