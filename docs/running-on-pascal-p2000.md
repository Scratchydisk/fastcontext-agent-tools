# Running on an old/small GPU via Ollama (Quadro P2000, 5 GB)

A record of getting FastContext-4B to run on a Quadro **P2000 (Pascal, compute
6.1, 5 GB)** — a card the normal vLLM path cannot use. It does run, but accuracy
is poor (see [Results](#results)); this is documented for completeness, not as a
recommended setup.

## Why the vLLM path (`serve-model.sh`) does not work here

- **Architecture.** Recent vLLM requires compute capability **7.0+**; Pascal is
  6.1, so vLLM refuses to start. FlashAttention / FlashInfer also need ≥7.5.
- **Quantisation.** `bitsandbytes` 4-bit (the 8 GB recipe) needs ≥7.0 too, so it
  won't load on Pascal.
- **Memory.** Full BF16 (~8 GB) doesn't fit 5 GB anyway.

The viable route on Pascal is **llama.cpp / Ollama** with a GGUF quant.

## The working recipe

### 1. An Ollama instance pinned to the P2000

If the box has more than one GPU, run a dedicated Ollama bound to the P2000 so it
doesn't fight the other card. As a systemd unit:

```ini
# /etc/systemd/system/ollama-p2000.service
Environment=CUDA_DEVICE_ORDER=PCI_BUS_ID
Environment=CUDA_VISIBLE_DEVICES=1          # the P2000's index
Environment=OLLAMA_HOST=0.0.0.0:11435
ExecStart=/usr/local/bin/ollama serve
```

### 2. Pull a Q4 GGUF (fits 5 GB)

A 4-bit GGUF of the 4B model is ~2.5 GB. Community uploads exist; this used:

```bash
OLLAMA_HOST=127.0.0.1:11435 ollama pull hf.co/mitkox/FastContext-1.0-4B-RL-Q4_K_M-GGUF
```

It loads on the P2000 (≈2.9 GB VRAM in use).

### 3. The thinking-mode fix (the actual blocker)

FastContext-RL is a **reasoning model**. Ollama routes its reasoning into a
separate `reasoning` field and leaves the OpenAI `content` empty — so FastContext
(which reads `content` and `tool_calls` over the `/v1` endpoint) receives nothing
and every explore comes back empty.

- `think: false` disables it on Ollama's **native** `/api/chat`, but the
  **`/v1` OpenAI endpoint ignores it** (tested on Ollama 0.30.6). Upgrading
  Ollama is **not** the fix.
- `/no_think` in the prompt did not work either with this GGUF's template.

The reliable fix is a **Modelfile that bakes "no-think" in** by prefilling an
empty `<think></think>` block, so generation goes straight to `content`:

```bash
OLLAMA_HOST=127.0.0.1:11435 ollama show hf.co/mitkox/FastContext-1.0-4B-RL-Q4_K_M-GGUF:latest --modelfile > fc.mf
# In the TEMPLATE, change the generation prefix
#     <|im_start|>assistant\n<think>\n
# to prefill an empty think block:
#     <|im_start|>assistant\n<think>\n\n</think>\n\n
echo "PARAMETER num_ctx 8192" >> fc.mf       # see "context" below
echo "PARAMETER temperature 0.2" >> fc.mf    # GGUF defaults to 0.6; 0.2 locates better
OLLAMA_HOST=127.0.0.1:11435 ollama create fastcontext-nothink -f fc.mf
```

After this, the `/v1` endpoint returns normal `content` and emits `tool_calls`.

### 3a. Raise the context window

Ollama defaults to `num_ctx 4096`, which is too small — `FC_MAX_TOKENS` alone is
~4000, leaving no room for the agent's prompt as it reads files. Add
`PARAMETER num_ctx 8192` to the Modelfile (above). On a 5 GB card the 3 GB model
plus an 8192 KV cache still fits.

### 3b. Make sure it actually runs on the GPU

`ollama ps` must show `100% GPU` in the PROCESSOR column. If it shows a
`CPU/GPU` split, the P2000's VRAM was already occupied (another model still
resident, ComfyUI, etc.) and Ollama offloaded layers to CPU — which tanks
performance and invalidates any benchmark. Free it first:

```bash
OLLAMA_HOST=127.0.0.1:11435 ollama stop <other-model>
nvidia-smi -i 1 --query-compute-apps=pid,used_memory --format=csv,noheader
# `ollama stop` sometimes leaves an orphaned llama-server; kill the stray PID
# directly (or restart the ollama service) until the P2000 is clear, then warm
# only this model:
OLLAMA_HOST=127.0.0.1:11435 ollama run fastcontext-nothink:latest "ok" --keepalive 2h
```

### 4. Point FastContext at it

```bash
export BASE_URL="http://<p2000-host>:11435/v1"   # or an SSH tunnel
export MODEL="fastcontext-nothink:latest"
export API_KEY=""                                # FastContext defaults to "ollama"
export FASTCONTEXT_EXPLORE_RETRIES=2             # recovers some empty answers
```

## Results

Tool-calling works after the no-think fix, but the Q4 4B model is weak on this
setup:

- It fumbles tool arguments (e.g. `Read` on a directory, `Grep` on a
  non-existent path).
- It frequently emits an **empty `<final_answer>`** — the prose answer lands in
  the message body but the citation block is empty, so nothing parses.
  `FASTCONTEXT_EXPLORE_RETRIES` recovers a fraction of these.

File-hit rate (clean GPU, 100% on-GPU, retry-on-empty, 2 iterations):

| | ctx 8192 | ctx 16384 |
|---|---|---|
| Q4_K_M | **5/10 (50%)** | timed out (>220 s/query) |
| Q6_K | **3/10 (30%)** | — (would time out) |

All well below the 8 GB quant (73%), 12 GB full (87%), and 24 GB full (73%)
configs. Two findings from this card specifically:

- **Higher quant did not help.** Q6_K (30%) did not beat Q4_K_M (50%) — the
  limiter is the small model's agentic competence, not quant precision.
- **More context made it worse.** 16384 timed out per query; 8192 is the
  practical ceiling on this card. KV-cache quantization could free memory but
  would not address the speed/quality bottleneck.

Per-query latency is also much higher than any other config. See
[benchmarks/results/5gb-p2000-ollama/](../benchmarks/results/5gb-p2000-ollama/)
and `5gb-p2000-q6/`.

**Verdict:** a proof that FastContext-4B *can* run on a 5 GB Pascal card, not a
practical configuration. Use a card that supports vLLM (≥ compute 7.0, ≥ 8 GB)
for real use.
