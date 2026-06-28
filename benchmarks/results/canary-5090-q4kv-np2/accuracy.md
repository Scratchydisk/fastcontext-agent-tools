# Accuracy benchmark

Run: 2026-06-28
Iterations per query: 3

- label: `canary-5090-q4kv-np2`
- endpoint: `http://127.0.0.1:30007/v1`
- model: `fc-canary:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 4/15**

| # | hits | files cited (any iter) | avg tool calls |
|---|------|------------------------|----------------|
| 1 | 1/3 | server.py | 4.0 |
| 2 | 0/3 | (none) | 10.0 |
| 3 | 0/3 | (none) | 12.0 |
| 4 | 0/3 | (none) | 12.0 |
| 5 | 3/3 | env.local.sh.example, fastcontext_cli.py, runtime.py | 22.0 |

A *hit* means a returned citation pointed at an accepted ground-truth file for that query. A miss returned either no citation or one on a different file. Results vary run to run (sampling); re-run to confirm.
