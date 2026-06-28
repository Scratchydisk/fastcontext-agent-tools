# Token-usage benchmark: with vs without FastContext

Run: 2026-06-28
Tokenizer: tiktoken o200k_base

- label: `8gb-a2000-quant`
- endpoint: `http://127.0.0.1:30001/v1`
- model: `microsoft/FastContext-1.0-4B-RL`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

All figures are tokens that enter the **main agent's context**.

| # | answered | WITH (ctx in) | WITHOUT inline-search | WITHOUT grep+read | reduction |
|---|----------|---------------|-----------------------|-------------------|-----------|
| 1 | yes | 536 | 5602 | 4617 (4f) | 10.5x |
| 2 | yes | 229 | 6109 | 4118 (3f) | 26.7x |
| 3 | yes | 210 | 9272 | 18489 (6f) | 44.2x |
| 4 | yes | 326 | 9977 | 20612 (10f) | 30.6x |
| 5 | yes | 318 | 13792 | 5611 (4f) | 43.4x |

**Answered queries (5/5):** 1619 tokens in WITH, vs 44752 (inline search) / 53447 (grep+read) WITHOUT.

**Context reduction: 27.6x (inline search), 33.0x (grep+read).**

Only answered queries count toward the reduction: a miss "saves" tokens but returns nothing, so it is not a real saving. This measures context cost (the mechanism); the ground-truth figure is a real Claude Code A/B comparing `/cost` on the same task with and without the tool. Re-run to confirm — sampling makes results vary.
