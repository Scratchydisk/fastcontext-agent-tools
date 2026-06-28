# Accuracy benchmark

Run: 2026-06-28
Iterations per query: 3

- label: `canary-5090-q4kv`
- endpoint: `http://127.0.0.1:30007/v1`
- model: `fc-canary:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 6/15**

| # | hits | files cited (any iter) | avg tool calls |
|---|------|------------------------|----------------|
| 1 | 1/3 | server.py | 3.0 |
| 2 | 2/3 | server.py | 5.3 |
| 3 | 2/3 | runtime.py | 20.7 |
| 4 | 1/3 | runtime.py | 29.0 |
| 5 | 0/3 | (none) | 31.0 |

A *hit* means a returned citation pointed at an accepted ground-truth file for that query. A miss returned either no citation or one on a different file. Results vary run to run (sampling); re-run to confirm.
