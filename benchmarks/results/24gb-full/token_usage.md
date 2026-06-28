# Token-usage benchmark: with vs without FastContext

Run: 2026-06-28
Tokenizer: tiktoken o200k_base

- label: `24gb-full`
- endpoint: `http://127.0.0.1:30002/v1`
- model: `microsoft/FastContext-1.0-4B-RL`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

All figures are tokens that enter the **main agent's context**.

| # | answered | WITH (ctx in) | WITHOUT inline-search | WITHOUT grep+read | reduction |
|---|----------|---------------|-----------------------|-------------------|-----------|
| 1 | yes | 594 | 5235 | 4617 (4f) | 8.8x |
| 2 | yes | 233 | 5504 | 4118 (3f) | 23.6x |
| 3 | yes | 218 | 7530 | 18489 (6f) | 34.5x |
| 4 | yes | 334 | 8574 | 12710 (10f) | 25.7x |
| 5 | yes | 334 | 10622 | 5611 (4f) | 31.8x |

**Answered queries (5/5):** 1713 tokens in WITH, vs 37465 (inline search) / 45545 (grep+read) WITHOUT.

**Context reduction: 21.9x (inline search), 26.6x (grep+read).**

Only answered queries count toward the reduction: a miss "saves" tokens but returns nothing, so it is not a real saving. This measures context cost (the mechanism); the ground-truth figure is a real Claude Code A/B comparing `/cost` on the same task with and without the tool. Re-run to confirm — sampling makes results vary.
