# Token-usage benchmark: with vs without FastContext

Run: 2026-06-28
Tokenizer: tiktoken o200k_base

- endpoint: `http://127.0.0.1:30000/v1`
- model: `microsoft/FastContext-1.0-4B-RL`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

All figures are tokens that enter the **main agent's context**.

| # | answered | WITH (ctx in) | WITHOUT inline-search | WITHOUT grep+read | reduction |
|---|----------|---------------|-----------------------|-------------------|-----------|
| 1 | yes | 418 | 5005 | 4617 (4f) | 12.0x |
| 2 | yes | 223 | 5274 | 4118 (3f) | 23.7x |
| 3 | yes | 210 | 9358 | 17508 (6f) | 44.6x |
| 4 | yes | 315 | 10344 | 11199 (10f) | 32.8x |
| 5 | yes | 432 | 13210 | 5389 (4f) | 30.6x |

**Answered queries (5/5):** 1598 tokens in WITH, vs 43191 (inline search) / 42831 (grep+read) WITHOUT.

**Context reduction: 27.0x (inline search), 26.8x (grep+read).**

Only answered queries count toward the reduction: a miss "saves" tokens but returns nothing, so it is not a real saving. This measures context cost (the mechanism); the ground-truth figure is a real Claude Code A/B comparing `/cost` on the same task with and without the tool. Re-run to confirm — sampling makes results vary.
