# Accuracy benchmark

Run: 2026-06-28
Iterations per query: 3

- endpoint: `http://127.0.0.1:30000/v1`
- model: `microsoft/FastContext-1.0-4B-RL`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 14/15**

| # | hits | files cited (any iter) | avg tool calls |
|---|------|------------------------|----------------|
| 1 | 3/3 | runtime.py, server.py | 17.0 |
| 2 | 3/3 | server.py | 36.0 |
| 3 | 2/3 | runtime.py | 50.3 |
| 4 | 3/3 | runtime.py | 61.7 |
| 5 | 3/3 | fastcontext_cli.py, runtime.py | 80.0 |

A *hit* means a returned citation pointed at an accepted ground-truth file for that query. A miss returned either no citation or one on a different file. Results vary run to run (sampling); re-run to confirm.
