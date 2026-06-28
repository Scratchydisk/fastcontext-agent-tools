# Token-usage benchmark: with vs without FastContext

Run: 2026-06-28
Tokenizer: tiktoken o200k_base

- label: `12gb-3060-full`
- endpoint: `http://127.0.0.1:30000/v1`
- model: `microsoft/FastContext-1.0-4B-RL`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

All figures are tokens that enter the **main agent's context**.

| # | answered | WITH (ctx in) | WITHOUT inline-search | WITHOUT grep+read | reduction |
|---|----------|---------------|-----------------------|-------------------|-----------|
| 1 | yes | 464 | 2040 | 4617 (4f) | 4.4x |
| 2 | yes | 318 | 2430 | 4118 (3f) | 7.6x |
| 3 | no | 115 | 4601 | 18489 (6f) | — |
| 4 | yes | 227 | 5422 | 12712 (10f) | 23.9x |
| 5 | yes | 325 | 7886 | 5611 (4f) | 24.3x |

**Answered queries (4/5):** 1334 tokens in WITH, vs 17778 (inline search) / 27058 (grep+read) WITHOUT.

**Context reduction: 13.3x (inline search), 20.3x (grep+read).**

Only answered queries count toward the reduction: a miss "saves" tokens but returns nothing, so it is not a real saving. This measures context cost (the mechanism); the ground-truth figure is a real Claude Code A/B comparing `/cost` on the same task with and without the tool. Re-run to confirm — sampling makes results vary.
