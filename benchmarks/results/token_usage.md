# Token-usage benchmark: with vs without FastContext

Run: 2026-06-28
Tokenizer: tiktoken o200k_base

- endpoint: `http://127.0.0.1:30000/v1`
- model: `microsoft/FastContext-1.0-4B-RL`
- FC_MAX_TOKENS: `4000`
- FASTCONTEXT_REROOT_PATHS: `1`

All figures are tokens that enter the **main agent's context**.

| # | answered | WITH (ctx in) | WITHOUT inline-search | WITHOUT grep+read | reduction |
|---|----------|---------------|-----------------------|-------------------|-----------|
| 1 | yes | 408 | 2409 | 4617 (4f) | 5.9x |
| 2 | no | 110 | 6863 | 4118 (3f) | — |
| 3 | yes | 218 | 8656 | 17427 (6f) | 39.7x |
| 4 | yes | 228 | 9338 | 11110 (10f) | 41.0x |
| 5 | yes | 488 | 12303 | 5389 (4f) | 25.2x |

**Answered queries (4/5):** 1342 tokens in WITH, vs 32706 (inline search) / 38543 (grep+read) WITHOUT.

**Context reduction: 24.4x (inline search), 28.7x (grep+read).**

Only answered queries count toward the reduction: a miss "saves" tokens but returns nothing, so it is not a real saving. This measures context cost (the mechanism); the ground-truth figure is a real Claude Code A/B comparing `/cost` on the same task with and without the tool. Re-run to confirm — sampling makes results vary.
