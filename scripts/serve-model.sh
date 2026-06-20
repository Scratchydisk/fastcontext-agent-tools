#!/usr/bin/env bash
# serve-model.sh — serve the FastContext model on a local OpenAI-compatible
# endpoint (port 30000) with vLLM, for the MCP server to call.
#
# Long-running. Run in its own terminal; wait for the Uvicorn
# "Application startup complete" line on :30000, then run
# ./scripts/kickoff.sh explore in another terminal.
#
# vLLM lives in its OWN venv ($FC_SERVE_VENV) so its heavy GPU deps never
# collide with the lightweight MCP venv.
#
# WHY THESE FLAGS: fastcontext/agent/llm.py reads server-side `tool_calls`,
# which vLLM only emits with --enable-auto-tool-choice + a tool parser.
# FastContext-4B is built on Qwen3-4B-Instruct, so `hermes` is correct. If
# explore returns no citations, try --tool-call-parser qwen3_xml.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/env.sh"

MODEL_ID="$MODEL"
# Model supports up to 262144; default smaller to keep KV cache modest. Override
# with CTX_LEN=... if your card has headroom.
CTX_LEN="${CTX_LEN:-65536}"

if [[ ! -x "$FC_SERVE_VENV/bin/python" ]]; then
  echo ">> creating serving venv ($FC_SERVE_VENV)"
  uv venv --python 3.12 "$FC_SERVE_VENV"
fi
source "$FC_SERVE_VENV/bin/activate"

if ! python -c "import vllm" 2>/dev/null; then
  echo ">> installing vLLM (large; pulls a CUDA PyTorch build for Blackwell)"
  uv pip install vllm
fi

echo ">> launching vLLM for $MODEL_ID (ctx=$CTX_LEN) on port 30000"
exec vllm serve "$MODEL_ID" \
    --port 30000 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes \
    --max-model-len "$CTX_LEN" \
    --gpu-memory-utilization 0.9 \
    --trust-remote-code
