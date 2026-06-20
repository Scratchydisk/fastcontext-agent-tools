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
| `scripts/env.local.sh` | **Gitignored.** Per-machine values: `FASTCONTEXT_ALLOWED_ROOTS`, `HF_TOKEN`, remote endpoint. |
| `scripts/kickoff.sh` | Install if needed → `--print-health` → optional live `explore` smoke test. |
| `scripts/serve-model.sh` | Launch vLLM for the model. Run in its own terminal. |

All paths are derived from the script location, so the repo can live anywhere.

## Checkpoint A — MCP works unchanged (no model needed)

```bash
./scripts/kickoff.sh          # creates .venv (py3.12), installs, prints health
```
Expect `"ok": true`, the bundled FastContext importing, and `python -m pytest`
passing (13/13).

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
- **Blackwell (RTX 5090, sm_120).** Verified with vLLM 0.23.0 + torch 2.11+cu130
  against driver/CUDA 13.x. The server resolves `Qwen3ForCausalLM` and loads
  with FlashAttention 2 / FlashInfer.
- **First-boot weight download.** Without `HF_TOKEN` the unauthenticated HF Hub
  pull can rate-limit/stall; set a token to make it reliable.
- **Context length** defaults to 65536 (`CTX_LEN` env to override); the model
  supports up to 262144 and a 24 GB card has room.

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

For serving the model on a separate machine, see the **Hosting the model on a
remote server** section in the [README](../README.md).
