# Accuracy benchmark

Run: 2026-06-28

- endpoint: `http://127.0.0.1:30000/v1`
- model: `microsoft/FastContext-1.0-4B-RL`
- FC_MAX_TOKENS: `4000`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 4/5**

| # | hit | files cited | warnings | tool calls |
|---|-----|-------------|----------|------------|
| 1 | YES | server.py | 1 | 11 |
| 2 | no | runtime.py | 0 | 23 |
| 3 | YES | runtime.py | 0 | 28 |
| 4 | YES | runtime.py | 0 | 31 |
| 5 | YES | fastcontext_cli.py, runtime.py | 0 | 37 |

A *hit* means a returned citation pointed at an accepted ground-truth file for that query. A miss returned either no citation or one on a different file. Results vary run to run (sampling); re-run to confirm.
