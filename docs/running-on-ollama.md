# Running the model via Ollama (GGUF)

An alternative to the vLLM path in [running-locally.md](running-locally.md).
Ollama serves a GGUF quant of FastContext-4B and exposes the same
OpenAI-compatible `/v1` endpoint the MCP server expects, so nothing downstream
changes: you point `BASE_URL` at Ollama instead of vLLM.

This is not a fallback for weak hardware. On the cards we tested, a Q4_K_M GGUF
under Ollama scored as well as or better than vLLM on the same card (15/15 on a
12 GB 3060, 14/15 on an 8 GB A2000, against 13/15 and 11/15 for vLLM). See
[benchmarks/EXPERIMENTS.md](../benchmarks/EXPERIMENTS.md) experiment 6.

When to pick Ollama over vLLM:

- You already run Ollama and don't want a second serving stack.
- You want the model to sit in a slice of a large card and leave the rest free
  for other work. A Q4 GGUF is ~2.5 GB of weights; even at a 16k context it is
  ~7.5 GB resident, so a 24 GB card has ~16 GB left over. (On a 12 GB card that
  same 7.5 GB is half the card, so the trade-off only really pays off on a big
  GPU.)
- Your GPU is too old for vLLM (compute < 7.0, e.g. a Pascal card). That case
  has its own write-up with extra steps: [running-on-pascal-p2000.md](running-on-pascal-p2000.md).

vLLM is still the better choice when you want maximum throughput, full BF16
precision, or the long contexts (65k+) that a big card can hold under vLLM.

## 1. Build a no-think GGUF model

FastContext-1.0-4B-RL is a reasoning model. Out of the box its GGUF emits a
`<think>` block, and depending on the Ollama version the answer either never
leaves the reasoning channel or never closes the think block, so the OpenAI
`content` field comes back empty and every explore returns nothing. The fix is a
Modelfile that prefills an empty think block, which sends generation straight to
`content`:

```bash
# pull a community Q4_K_M GGUF of the 4B model (~2.5 GB)
ollama pull hf.co/mitkox/FastContext-1.0-4B-RL-Q4_K_M-GGUF

# dump its Modelfile
ollama show hf.co/mitkox/FastContext-1.0-4B-RL-Q4_K_M-GGUF:latest --modelfile > fc.mf

# in the TEMPLATE, change the assistant generation prefix from
#     <|im_start|>assistant\n<think>\n
# to a prefilled, closed think block:
#     <|im_start|>assistant\n<think>\n\n</think>\n\n

# set the context window (see step 2)
echo "PARAMETER num_ctx 16384" >> fc.mf

ollama create fc-q4-nothink-16k -f fc.mf
```

Verify the model returns content and makes tool calls before wiring it up. The
smoke-test query in the [README](../README.md#test-it) is the quickest check; an
empty `<final_answer>` means the no-think edit didn't take (or the KV-quant trap
below).

## 2. Context window vs VRAM

Ollama defaults to `num_ctx 4096`, which is too small here: `FC_MAX_TOKENS` alone
is ~4000, leaving no room for the agent's prompt as it reads files. Raise it in
the Modelfile. The KV cache grows roughly linearly with `num_ctx`, so this is the
main lever on resident memory:

| `num_ctx` | Approx. resident (Q4_K_M, fp16 KV) |
|---|---|
| 8192 | ~5.5 GB |
| 16384 | ~7.5 GB |
| 32768 | ~11 GB |

16384 is a good default and matches the context used in the benchmarks. On a
small card drop to 8192; on a 24 GB card you can raise it and still leave plenty
free for other workloads.

## 3. Do not quantise the KV cache

Ollama can quantise the KV cache (`OLLAMA_KV_CACHE_TYPE=q8_0` or `q4_0`) to save
memory. **Do not use `q4_0` for this workload.** A 4-bit KV cache degrades
attention enough that the model stops emitting tool calls entirely: it answers
from nothing in prose and leaves `<final_answer>` empty. On a 12 GB 3060 the same
model and context went from 15/15 with an fp16 KV cache to 0/15 with `q4_0`. The
~2 GB it saves is not worth a total failure. Leave the KV cache at fp16.

Flash attention on its own (`OLLAMA_FLASH_ATTENTION=1`, fp16 KV) is fine and
slightly faster.

## 4. Pin to a specific GPU (multi-GPU boxes)

If the box has more than one GPU, run a dedicated Ollama bound to the card you
want so it doesn't land on the wrong one. As a systemd unit:

```ini
# /etc/systemd/system/ollama.service.d/override.conf
[Service]
Environment="CUDA_DEVICE_ORDER=PCI_BUS_ID"
Environment="CUDA_VISIBLE_DEVICES=0"        # the target card's index
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_KEEP_ALIVE=3h"
# do NOT set OLLAMA_KV_CACHE_TYPE (see step 3)
```

Then warm the model and confirm it sits entirely on the GPU:

```bash
ollama run fc-q4-nothink-16k:latest "ok" --keepalive 3h
ollama ps        # PROCESSOR must read 100% GPU, not a CPU split
```

A CPU/GPU split means the card had VRAM occupied at load time. Free it (stop the
other model; check `nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader`
for stray runners and kill them) and re-warm. Stopping an Ollama instance
sometimes leaves an orphaned llama-runner holding VRAM; kill that PID directly.

## 5. Point FastContext at it

Same as any remote endpoint. Over an SSH tunnel:

```bash
ssh -f -N -L 30000:127.0.0.1:11434 gpuhost
```

Then in the MCP env block (not `env.local.sh`, which the MCP client doesn't
read):

```json
"env": {
  "BASE_URL": "http://127.0.0.1:30000/v1",
  "MODEL": "fc-q4-nothink-16k:latest",
  "API_KEY": "ollama",
  "FC_TEMPERATURE": "0.2",
  "FASTCONTEXT_REROOT_PATHS": "1",
  "FASTCONTEXT_EXPLORE_RETRIES": "2"
}
```

Reconnect the client and `fastcontext_health` should pass.

## Quant choice

Q4_K_M is the sweet spot. Q6_K was worse on every card we tried (9/15 vs 14/15
on the A2000, 3/10 vs 5/10 on the P2000) and slower, because the limiter is the
small model's tool-use competence, not quant precision. Don't reach for a higher
quant expecting better accuracy.
