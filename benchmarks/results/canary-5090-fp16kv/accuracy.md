# Accuracy benchmark

Run: 2026-06-28
Iterations per query: 3

- label: `canary-5090-fp16kv`
- endpoint: `http://127.0.0.1:30007/v1`
- model: `fc-canary:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 11/15** (1 attempt(s) timed out, counted as misses)

| # | hits | files cited (any iter) | avg tool calls |
|---|------|------------------------|----------------|
| 1 | 3/3 | runtime.py, server.py | 14.0 |
| 2 | 1/3 | runtime.py, server.py | 61.7 |
| 3 | 2/3 | runtime.py | 53.3 |
| 4 | 2/3 | runtime.py, test_server.py | 90.3 |
| 5 | 3/3 | fastcontext_cli.py, runtime.py | 103.7 |

A *hit* means a returned citation pointed at an accepted ground-truth file for that query. A miss returned either no citation or one on a different file. Results vary run to run (sampling); re-run to confirm.
