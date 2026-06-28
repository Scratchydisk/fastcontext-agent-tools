# Accuracy benchmark

Run: 2026-06-28
Iterations per query: 2

- label: `5gb-p2000-q6`
- endpoint: `http://127.0.0.1:30003/v1`
- model: `fastcontext-q6-nothink:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 3/10**

| # | hits | files cited (any iter) | avg tool calls |
|---|------|------------------------|----------------|
| 1 | 2/2 | server.py | 5.5 |
| 2 | 0/2 | (none) | 7.0 |
| 3 | 1/2 | runtime.py, server.py | 8.5 |
| 4 | 0/2 | (none) | 10.0 |
| 5 | 0/2 | (none) | 10.0 |

A *hit* means a returned citation pointed at an accepted ground-truth file for that query. A miss returned either no citation or one on a different file. Results vary run to run (sampling); re-run to confirm.
