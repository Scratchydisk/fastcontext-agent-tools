# FastContext Agent Tools

MCP server and Codex skill for using Microsoft's FastContext as a read-only
repository exploration subagent.

![Architecture](docs/assets/architecture.svg)

FastContext answers one narrow question for a coding agent:

> Which files and line ranges should the main agent inspect before solving this task?

This repository provides the complete integration:

- `fastcontext-mcp`: a Python stdio MCP server that installs Microsoft FastContext as a pinned runtime dependency.
- `skills/fastcontext-explorer`: a Codex skill that teaches an agent when to delegate repository exploration.
- MCP setup guides in English, Traditional Chinese, and Japanese.

It does not bundle model weights, run inference, or modify repositories. The MCP
server runs the bundled `fastcontext.cli` module in the same Python environment
and returns candidate file-line citations for the main agent to verify.

## About this fork

This is a maintained fork of [`Jakevin/fastcontext-agent-tools`](https://github.com/Jakevin/fastcontext-agent-tools).
It adds, on top of upstream:

- **Local + small-GPU serving** — `scripts/serve-model.sh` and friends run the
  model under vLLM, with opt-in flags (`QUANT`, `GPU_MEM_UTIL`, `ENFORCE_EAGER`,
  `CTX_LEN`, `FASTCONTEXT_REROOT_PATHS`) that make FastContext-4B usable on an
  8 GB card. All flags are off by default, so larger GPUs keep upstream
  behaviour. See [docs/running-locally.md](docs/running-locally.md).
- **MCP stdio framing fix** — the server speaks newline-delimited JSON per the
  MCP spec (upstream used LSP-style `Content-Length` framing, which spec-compliant
  clients like Claude Code cannot connect to).
- **Path re-rooting** for heavily-quantised models that mangle the workspace path
  in tool arguments and citations.

It pins `microsoft/fastcontext` at commit
[`1522d6d`](https://github.com/microsoft/fastcontext/tree/1522d6d6b5e040e817b468e12826662aa069a8b0),
which incorporates five fixes reported from this work (microsoft/fastcontext
issues #18–#22: ReadTool path traversal, GrepTool cwd, configurable max tokens,
ripgrep validation, negative read offset). Those upstream fixes let the fork drop
its earlier monkeypatch workarounds; only the framing fix and the quantised-model
re-rooting remain fork-specific. The corresponding PRs against the upstream
wrapper repo are open but unmerged.

## One-Line LLM Agent Install Prompt

Ask an LLM agent:

> Install FastContext Agent Tools from `https://github.com/Jakevin/fastcontext-agent-tools`; its package installation includes Microsoft FastContext. Configure `python -m fastcontext_mcp` as a stdio MCP server with `BASE_URL`, `MODEL`, `API_KEY`, and `FASTCONTEXT_ALLOWED_ROOTS`, then enable `skills/fastcontext-explorer`.

Direct install command for Codex-style local skills:

```bash
git clone https://github.com/Jakevin/fastcontext-agent-tools && cd fastcontext-agent-tools && python -m pip install -e . && mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills" && ln -sfn "$(pwd)/skills/fastcontext-explorer" "${CODEX_HOME:-$HOME/.codex}/skills/fastcontext-explorer"
```

## Why This Exists

Microsoft FastContext separates repository exploration from code solving. The
upstream project describes a dedicated explorer that uses read-only `READ`,
`GLOB`, and `GREP` tools, issues parallel tool calls, and returns compact
`<final_answer>` citations. Microsoft reports Mini-SWE-Agent integration gains
of up to 5.5 score improvement and up to 60% main-agent token reduction.

Primary sources:

- Microsoft FastContext: <https://github.com/microsoft/fastcontext>
- Model card: <https://huggingface.co/microsoft/FastContext-1.0-4B-SFT>
- Paper: <https://arxiv.org/abs/2606.14066>

## Quick Install

```bash
git clone https://github.com/Jakevin/fastcontext-agent-tools
cd fastcontext-agent-tools
python -m pip install -e .
python -m fastcontext_mcp --print-health
```

If your Python scripts directory is on `PATH`, `fastcontext-mcp --print-health`
works too.

## Requirements

- Python 3.12+.
- An OpenAI-compatible endpoint serving a FastContext-compatible model.

Installing this package also installs Microsoft FastContext from the pinned
official source revision. No separate FastContext checkout or CLI installation
is required.

Endpoint environment:

```bash
export BASE_URL="http://127.0.0.1:30000/v1"
export MODEL="microsoft/FastContext-1.0-4B-SFT"
export API_KEY="your-api-key"
export FASTCONTEXT_ALLOWED_ROOTS="/path/to/repos"
```

`FASTCONTEXT_ALLOWED_ROOTS` is an `os.pathsep` separated allowlist. If unset,
the MCP server only allows repositories under the directory where the server was
started.

## MCP Configuration

Example stdio config:

```json
{
  "mcpServers": {
    "fastcontext": {
      "command": "python",
      "args": ["-m", "fastcontext_mcp"],
      "env": {
        "BASE_URL": "http://127.0.0.1:30000/v1",
        "MODEL": "microsoft/FastContext-1.0-4B-SFT",
        "API_KEY": "your-api-key",
        "FASTCONTEXT_ALLOWED_ROOTS": "/path/to/repos"
      }
    }
  }
}
```

Localized MCP guides:

- Traditional Chinese: [docs/mcp.zh-TW.md](docs/mcp.zh-TW.md)
- Japanese: [docs/mcp.ja.md](docs/mcp.ja.md)

## MCP Tools

### `fastcontext_health`

Checks whether the bundled `fastcontext.cli` module is importable and whether
the endpoint environment is set.

### `fastcontext_explore`

Runs FastContext against a repository and returns parsed citations plus raw
output.

```json
{
  "repo_path": "/path/to/repo",
  "query": "Locate the request validation logic for uploaded files",
  "max_turns": 6,
  "citation": true,
  "timeout_seconds": 300
}
```

### `fastcontext_explore_with_trace`

Same as `fastcontext_explore`, but saves a FastContext JSONL trajectory. Relative
`trajectory_path` values are resolved inside `repo_path`.

## Codex Skill

The bundled skill lives at:

```text
skills/fastcontext-explorer
```

Install by copying or symlinking that folder into your Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$(pwd)/skills/fastcontext-explorer" "${CODEX_HOME:-$HOME/.codex}/skills/fastcontext-explorer"
```

Use the skill when a coding task requires repository localization before
editing. FastContext citations are candidate evidence; the main agent should
still read the cited files before changing code.

Additional project report:

- Full report: [docs/REPORT.md](docs/REPORT.md)

## Local deployment (this fork)

Helper scripts for running the whole thing locally live in `scripts/`
(`env.sh`, `serve-model.sh`, `kickoff.sh`); see
[docs/running-locally.md](docs/running-locally.md) for the full guide. The setup
is two independent processes:

1. **Model server** — vLLM serving `FastContext-1.0-4B-RL` on an
   OpenAI-compatible endpoint at `http://127.0.0.1:30000/v1`. Long-running, GPU.
2. **MCP server** — `python -m fastcontext_mcp`, spawned over stdio by the agent
   client. Lightweight (no torch); shells out to the bundled `fastcontext.cli`,
   which calls the model server and returns citations.

Note on where files are read: the `READ`/`GLOB`/`GREP` tools run **inside the
`fastcontext.cli` process** (the MCP box), not on the model server. The model
server only does inference. So the repository being explored must live on the
machine running the MCP, and `FASTCONTEXT_ALLOWED_ROOTS` is always local.

### Status so far

- **Checkpoint A — MCP works unchanged: verified.** Clean Python 3.12 venv (via
  `uv`), `pip install -e .` pulls the SHA-pinned Microsoft FastContext
  (`fastcontext==0.1.0`, lightweight: openai/httpx/pydantic, no torch),
  `--print-health` returns `"ok": true`, and the bundled test suite passes
  (13/13).
- **Model serving — stack confirmed for Blackwell.** vLLM 0.23.0 with
  torch 2.11+cu130 runs on the RTX 5090 Laptop (sm_120); the server starts,
  resolves `Qwen3ForCausalLM`, and loads weights with FlashAttention 2 /
  FlashInfer kernels. Launched with `--enable-auto-tool-choice
  --tool-call-parser hermes` (required — `llm.py` reads server-side
  `tool_calls`).
- **Live `explore` — not yet verified.** First-boot weight download from the HF
  Hub stalled (unauthenticated rate limit); set `HF_TOKEN` to make the initial
  pull reliable, then re-run `serve-model.sh` and `./kickoff.sh explore`.

### Run it

```bash
# terminal 1 — serve the model (first run downloads ~8 GB of weights)
export HF_TOKEN=hf_...               # recommended; avoids the unauthenticated stall
./scripts/serve-model.sh             # wait for "Application startup complete" on :30000

# terminal 2 — health + a live explore against a repo
./scripts/kickoff.sh                 # Checkpoint A (no model needed)
./scripts/kickoff.sh explore         # Checkpoint B (needs the model server above)
```

If `explore` returns no citations, the tool-call parser is the first suspect —
try `--tool-call-parser qwen3_xml` in `serve-model.sh`.

## Hosting the model on a remote server

Only the **inference** moves to the remote box; the MCP server and the
`fastcontext.cli` (which reads your repo files) stay local. So the remote host
needs the GPU and the model; your laptop keeps the repos.

**On the remote GPU host:**

```bash
uv pip install vllm
vllm serve microsoft/FastContext-1.0-4B-RL \
    --host 0.0.0.0 --port 30000 \
    --enable-auto-tool-choice --tool-call-parser hermes \
    --max-model-len 65536 --gpu-memory-utilization 0.9 \
    --trust-remote-code \
    --api-key "$REMOTE_API_KEY"          # require auth, since it's network-exposed
```

**On the local box (MCP/agent client):** point the four env vars at the remote
endpoint — everything else is unchanged:

```bash
export BASE_URL="https://fastcontext.example.com/v1"   # remote host (see TLS note)
export MODEL="microsoft/FastContext-1.0-4B-RL"
export API_KEY="$REMOTE_API_KEY"                       # must match the server's --api-key
export FASTCONTEXT_ALLOWED_ROOTS="/home/you/git"       # still LOCAL — repos live here
```

**What needs doing for a safe remote setup:**

- **Transport security.** vLLM serves plain HTTP with no TLS. Don't expose
  `:30000` directly. Either (a) put it behind a reverse proxy (nginx/Caddy) that
  terminates TLS and forwards to `127.0.0.1:30000`, then use an `https://` BASE_URL,
  or (b) keep vLLM bound to localhost on the remote host and reach it over an SSH
  tunnel (`ssh -L 30000:127.0.0.1:30000 gpuhost`), leaving BASE_URL as
  `http://127.0.0.1:30000/v1`.
- **Authentication.** Set `--api-key` on the server and the matching `API_KEY`
  locally. Without it, anyone who can reach the port can use your GPU.
- **Firewall.** Restrict the port to known clients (security group / ufw), even
  behind a proxy.
- **Latency & timeouts.** Each `fastcontext_explore` is a multi-turn loop, so
  every turn is a network round trip to the remote model. Keep the host close
  (region/VPN), and raise `timeout_seconds` on the tool call if the link is slow.
- **VRAM sizing.** The 4B model needs ~8 GB plus KV cache; raise
  `--max-model-len` toward 262144 only if the remote card has the headroom.
- **Alternative:** any OpenAI-compatible managed endpoint that hosts the model
  works too — just set `BASE_URL`/`API_KEY`/`MODEL` accordingly; no other change.

## Development

Run tests:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

Validate the bundled Codex skill:

```bash
python /path/to/skill-creator/scripts/quick_validate.py skills/fastcontext-explorer
```

## Safety Notes

- The MCP server exposes no edit/write tools.
- `repo_path` must resolve under `FASTCONTEXT_ALLOWED_ROOTS`.
- Secrets are read from environment variables only.
- Trajectories are written only when requested.

## License

MIT
