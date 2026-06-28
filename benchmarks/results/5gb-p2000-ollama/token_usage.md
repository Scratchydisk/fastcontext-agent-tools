# Token-usage benchmark: with vs without FastContext

Run: 2026-06-28
Tokenizer: tiktoken o200k_base

- label: `5gb-p2000-ollama`
- endpoint: `http://127.0.0.1:30003/v1`
- model: `fastcontext-nothink:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

All figures are tokens that enter the **main agent's context**.

| # | answered | WITH (ctx in) | WITHOUT inline-search | WITHOUT grep+read | reduction |
|---|----------|---------------|-----------------------|-------------------|-----------|
| 1 | no | 803 | 24 | 4617 (4f) | — |
| 2 | no | 805 | 24 | 4118 (3f) | — |
| 3 | yes | 392 | 2766 | 19966 (7f) | 7.1x |
| 4 | yes | 387 | 3360 | 12951 (10f) | 8.7x |
| 5 | no | 115 | 3360 | 5611 (4f) | — |

**Answered queries (2/5):** 779 tokens in WITH, vs 6126 (inline search) / 32917 (grep+read) WITHOUT.

**Context reduction: 7.9x (inline search), 42.3x (grep+read).**

Only answered queries count toward the reduction: a miss "saves" tokens but returns nothing, so it is not a real saving. This measures context cost (the mechanism); the ground-truth figure is a real Claude Code A/B comparing `/cost` on the same task with and without the tool. Re-run to confirm — sampling makes results vary.
